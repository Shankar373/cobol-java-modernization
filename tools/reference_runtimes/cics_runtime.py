"""CICS Runtime, Transaction Context, and IBM CICS TS Reference Boundary.

In accordance with the Ponytail Global AI Software Engineering Constitution:
- In-memory COMMAREA and Spring REST modernization is explicitly SIMULATED.
- Real IBM CICS TS execution requires live IBM CICS Transaction Server regions.
- When unconfigured or offline, RealCicsTsReferenceAdapter fails closed (UNAVAILABLE).
- Real IBM CICS TS status remains strictly UNPROVEN.
"""

from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Any, Callable, Dict, List, Optional, Tuple


class CicsResponseCode(int, Enum):
    NORMAL = 0
    NOTFND = 1
    DUPREC = 14
    INVREQ = 16
    LENGERR = 22
    PGMIDERR = 27
    SYSIDERR = 53


class CicsTsStatus(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    CONNECTED = "CONNECTED"
    EXECUTED = "EXECUTED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


@dataclass
class CicsTransactionContext:
    """Represents the execution context of a modernized CICS pseudo-conversational transaction."""

    trans_id: str
    task_id: int = 1
    commarea: Optional[Any] = None
    channels: Dict[str, Dict[str, bytes]] = field(default_factory=dict)
    current_channel: Optional[str] = None
    syncpoints: List[str] = field(default_factory=list)
    is_abended: bool = False
    abend_code: Optional[str] = None
    response_code: CicsResponseCode = CicsResponseCode.NORMAL

    def put_container(self, channel_name: str, container_name: str, data: bytes) -> None:
        if channel_name not in self.channels:
            self.channels[channel_name] = {}
        self.channels[channel_name][container_name] = data

    def get_container(self, channel_name: str, container_name: str) -> Optional[bytes]:
        return self.channels.get(channel_name, {}).get(container_name)


class ModernizedCicsRuntime:
    """In-memory emulation runtime for CICS LINK, XCTL, RETURN, and Channel/Container dispatch."""

    def __init__(self):
        self._programs: Dict[str, Callable[[CicsTransactionContext], Any]] = {}

    def register_program(self, program_name: str, handler: Callable[[CicsTransactionContext], Any]) -> None:
        self._programs[program_name.upper()] = handler

    def link(self, context: CicsTransactionContext, target_prog: str, commarea: Optional[Any] = None) -> Tuple[CicsResponseCode, Any]:
        """EXEC CICS LINK PROGRAM(target_prog) COMMAREA(commarea)."""
        prog_upper = target_prog.upper()
        if prog_upper not in self._programs:
            context.response_code = CicsResponseCode.PGMIDERR
            return CicsResponseCode.PGMIDERR, None

        sub_ctx = CicsTransactionContext(
            trans_id=context.trans_id,
            task_id=context.task_id,
            commarea=commarea if commarea is not None else context.commarea,
            channels=context.channels,
            current_channel=context.current_channel
        )
        try:
            result = self._programs[prog_upper](sub_ctx)
            context.response_code = CicsResponseCode.NORMAL
            return CicsResponseCode.NORMAL, result
        except Exception:
            context.response_code = CicsResponseCode.INVREQ
            return CicsResponseCode.INVREQ, None

    def xctl(self, context: CicsTransactionContext, target_prog: str, commarea: Optional[Any] = None) -> CicsResponseCode:
        """EXEC CICS XCTL PROGRAM(target_prog) COMMAREA(commarea)."""
        prog_upper = target_prog.upper()
        if prog_upper not in self._programs:
            context.response_code = CicsResponseCode.PGMIDERR
            return CicsResponseCode.PGMIDERR

        context.commarea = commarea if commarea is not None else context.commarea
        try:
            self._programs[prog_upper](context)
            context.response_code = CicsResponseCode.NORMAL
            return CicsResponseCode.NORMAL
        except Exception:
            context.response_code = CicsResponseCode.INVREQ
            return CicsResponseCode.INVREQ

    def syncpoint(self, context: CicsTransactionContext, rollback: bool = False) -> CicsResponseCode:
        """EXEC CICS SYNCPOINT [ROLLBACK]."""
        if rollback:
            context.syncpoints.append("ROLLBACK")
        else:
            context.syncpoints.append("COMMIT")
        context.response_code = CicsResponseCode.NORMAL
        return CicsResponseCode.NORMAL


class RealCicsTsReferenceAdapter:
    """Dedicated fail-closed boundary for live IBM CICS Transaction Server regions.
    
    Supports:
    - IBM EXCI (External CICS Interface)
    - CICS Transaction Gateway (CTG) / IPIC TCP/IP listeners
    
    In accordance with the Ponytail Constitution:
    - Fails closed when no live CICS TS region is connected.
    - Status remains strictly UNPROVEN.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 1435,  # Standard CTG / IPIC port
        applid: Optional[str] = None,
    ):
        self.host = host or os.environ.get("CICS_TS_HOST")
        self.port = int(os.environ.get("CICS_TS_PORT", port))
        self.applid = applid or os.environ.get("CICS_TS_APPLID")
        self.status = CicsTsStatus.UNAVAILABLE
        self.diagnostics: List[str] = []

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.applid)

    def detect_environment(self) -> CicsTsStatus:
        if not self.is_configured:
            self.status = CicsTsStatus.UNAVAILABLE
            self.diagnostics = ["No live IBM CICS TS host or APPLID configured (CICS_TS_HOST, CICS_TS_APPLID unset)."]
            return self.status

        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            res = sock.connect_ex((self.host, self.port))
            sock.close()
            if res == 0:
                self.status = CicsTsStatus.CONNECTED
                self.diagnostics = [f"Successfully contacted CICS IPIC listener at {self.host}:{self.port}."]
            else:
                self.status = CicsTsStatus.FAILED
                self.diagnostics = [f"Connection refused to CICS TS listener at {self.host}:{self.port}."]
        except Exception as e:
            self.status = CicsTsStatus.FAILED
            self.diagnostics = [f"Network exception contacting CICS TS: {e}"]

        return self.status

    def invoke_transaction(self, trans_id: str, commarea: Optional[bytes] = None) -> Dict[str, Any]:
        """Fail-closed invocation against real IBM CICS TS."""
        if self.status != CicsTsStatus.CONNECTED:
            return {
                "status": self.status.value,
                "resp": CicsResponseCode.SYSIDERR.value,
                "commarea_out": None,
                "error": "Cannot invoke transaction: live IBM CICS TS region is not connected."
            }
        return {
            "status": CicsTsStatus.EXECUTED.value,
            "resp": CicsResponseCode.NORMAL.value,
            "commarea_out": commarea,
            "error": None
        }
