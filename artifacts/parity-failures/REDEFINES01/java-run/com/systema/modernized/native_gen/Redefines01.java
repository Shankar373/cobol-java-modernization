package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Redefines01 {

    public int return_code = 0;
    public String out_rec = "          ";
    public String ws_fs = "  ";
    public String ws_display = "                    ";
    // --- REDEFINES Backing Storage ---
    private final byte[] ws_buf_x_backing = new byte[10];
    {
        java.util.Arrays.fill(ws_buf_x_backing, (byte) 32);
    }

    // --- REDEFINES Accessors ---
    public String get_ws_buf_x() {
        int off = 0;
        return new String(ws_buf_x_backing, off, 10, java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    public void set_ws_buf_x(String val) {
        int off = 0;
        if (val == null) val = "";
        String padded = padString(val, 10);
        byte[] src = padded.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        System.arraycopy(src, 0, ws_buf_x_backing, off, 10);
    }

    public Long get_ws_buf_9() {
        int off = 0;
        return (long) new com.systema.modernized.runtime.CobolNumeric(ws_buf_x_backing, off, 10, new com.systema.modernized.runtime.CobolNumericSpec(false, 10, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).getValue().longValue();
    }

    public void set_ws_buf_9(Long val) {
        int off = 0;
        new com.systema.modernized.runtime.CobolNumeric(ws_buf_x_backing, off, 10, new com.systema.modernized.runtime.CobolNumericSpec(false, 10, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).assign(java.math.BigDecimal.valueOf(val));
    }

    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }


    private String resolve_path_out_file() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("OUT-FILE");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("/run/WS-FILE-OUT");
        }
        if (resolvedPath == null) {
            String cleanLogical = "OUT-FILE";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "/run/WS-FILE-OUT";
        }
        return resolvedPath;
    }

    private java.io.InputStream out_file_stream_in;
    private java.io.OutputStream out_file_stream_out;

    private void open_out_file() {
        open_out_file("OUTPUT");
    }

    private void open_out_file(String mode) {
        try {
            close_out_file();
            if ("INPUT".equalsIgnoreCase(mode)) {
                out_file_stream_in = new java.io.BufferedInputStream(new java.io.FileInputStream(resolve_path_out_file()));
            } else if ("OUTPUT".equalsIgnoreCase(mode)) {
                java.nio.file.Path parent = Paths.get(resolve_path_out_file()).getParent();
                if (parent != null) Files.createDirectories(parent);
                out_file_stream_out = new java.io.BufferedOutputStream(new java.io.FileOutputStream(resolve_path_out_file()));
            }
            ws_fs = "00";
        } catch (IOException e) {
            ws_fs = "35";
        }
    }

    private boolean read_out_file() {
        try {
            if (out_file_stream_in == null) return false;
            byte[] buf = new byte[10];
            int bytesRead = 0;
            while (bytesRead < 10) {
                int r = out_file_stream_in.read(buf, bytesRead, 10 - bytesRead);
                if (r == -1) break;
                bytesRead += r;
            }
            if (bytesRead < 10) {
                ws_fs = "10";
                return false;
            }
            out_rec = new String(buf, 0, 10, java.nio.charset.StandardCharsets.ISO_8859_1);
            ws_fs = "00";
            return true;
        } catch (IOException e) {
            ws_fs = "30";
            return false;
        }
    }

    private void write_out_file() {
        try {
            if (out_file_stream_out == null) return;
            byte[] buf = new byte[10];
            byte[] c_out_rec = padString(out_rec, 10).getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
            System.arraycopy(c_out_rec, 0, buf, 0, Math.min(c_out_rec.length, 10));
            out_file_stream_out.write(buf);
            out_file_stream_out.flush();
            ws_fs = "00";
        } catch (IOException e) {
            ws_fs = "30";
        }
    }

    private void close_out_file() {
        try {
            if (out_file_stream_in != null) { out_file_stream_in.close(); out_file_stream_in = null; }
            if (out_file_stream_out != null) { out_file_stream_out.close(); out_file_stream_out = null; }
            ws_fs = "00";
        } catch (IOException e) {
            ws_fs = "30";
        }
    }

    private boolean programExited = false;
    private int nextParagraphIndex = -1;
    private boolean skipToNextSentence = false;
    private final int total_paras = 1;

    public static class StopRunException extends RuntimeException {}

    private int getParagraphIndex(String name) {
        if (name == null) return -1;
        switch (name) {
            case "main_para": return 0;
            default: return -1;
        }
    }

    private void runParagraph(int idx) {
        if (programExited) return;
        switch (idx) {
            case 0: main_para(); break;
            default: break;
        }
    }

    private void perform(String target, String thru) {
        int startIdx = getParagraphIndex(target);
        int endIdx = (thru != null) ? getParagraphIndex(thru) : startIdx;
        if (startIdx == -1 || endIdx == -1 || startIdx > endIdx) return;
        int i = startIdx;
        while (i <= endIdx) {
            if (programExited) return;
            nextParagraphIndex = -1;
            runParagraph(i);
            if (nextParagraphIndex != -1) {
                if (nextParagraphIndex >= startIdx && nextParagraphIndex <= endIdx) {
                    i = nextParagraphIndex;
                } else {
                    return;
                }
            } else {
                i++;
            }
        }
    }

    public void execute() {
        int i = 0;
        while (i < 1) {
            if (programExited) break;
            nextParagraphIndex = -1;
            runParagraph(i);
            if (nextParagraphIndex != -1) {
                i = nextParagraphIndex;
            } else {
                i++;
            }
        }
    }

    private void main_para() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { set_ws_buf_x(padString(String.valueOf("HELLO1234"), 10)); }
        if (!skipToNextSentence) {
            {
                    writeBytes("WS-BUF-9 as numeric: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(new com.systema.modernized.runtime.CobolNumeric(java.math.BigDecimal.valueOf(get_ws_buf_9()), new com.systema.modernized.runtime.CobolNumericSpec(false, 10, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).toDisplayString().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) { ws_display = padString(String.valueOf(String.valueOf(BigDecimal.valueOf(get_ws_buf_9()))), 20); }
        if (!skipToNextSentence) {
            {
                    writeBytes("WS-DISPLAY (buf redefines view): ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(ws_display.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) { set_ws_buf_9(9999999999L); }
        if (!skipToNextSentence) {
            {
                    writeBytes("After MOVE 9999999999 to WS-BUF-9:".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) {
            {
                    writeBytes("WS-BUF-X: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(get_ws_buf_x().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) {
            {
                    writeBytes("WS-BUF-9: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(new com.systema.modernized.runtime.CobolNumeric(java.math.BigDecimal.valueOf(get_ws_buf_9()), new com.systema.modernized.runtime.CobolNumericSpec(false, 10, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).toDisplayString().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) { out_rec = padString(String.valueOf(get_ws_buf_x()), 10); }
        if (!skipToNextSentence) { open_out_file("OUTPUT"); }
        if (!skipToNextSentence) { write_out_file(); }
        if (!skipToNextSentence) { close_out_file(); }
        if (!skipToNextSentence) { if (true) { throw new StopRunException(); } }
    }

    public static void main(String[] args) {
        try {
            new Redefines01().execute();
        } catch (StopRunException e) {
            System.exit(0);
        }
    }

    private static String formatSigned(long value, int length, boolean signed) {
        if (!signed) {
            return String.format("%0" + length + "d", Math.abs(value));
        }
        if (value >= 0) {
            return String.format("%0" + length + "d", value);
        } else {
            long absVal = Math.abs(value);
            String absStr = String.format("%0" + length + "d", absVal);
            char lastChar = absStr.charAt(absStr.length() - 1);
            char signChar;
            switch (lastChar) {
                case '0': signChar = 'p'; break;
                case '1': signChar = 'q'; break;
                case '2': signChar = 'r'; break;
                case '3': signChar = 's'; break;
                case '4': signChar = 't'; break;
                case '5': signChar = 'u'; break;
                case '6': signChar = 'v'; break;
                case '7': signChar = 'w'; break;
                case '8': signChar = 'x'; break;
                case '9': signChar = 'y'; break;
                default: signChar = lastChar;
            }
            return absStr.substring(0, absStr.length() - 1) + signChar;
        }
    }

    private static BigDecimal parseSigned(String val, int scale) {
        if (val == null || val.trim().isEmpty()) {
            return BigDecimal.ZERO;
        }
        val = val.trim();
        char last = val.charAt(val.length() - 1);
        boolean negative = false;
        char replacement = last;
        if (last >= 'p' && last <= 'y') {
            negative = true;
            replacement = (char) ('0' + (last - 'p'));
        }
        String cleanVal = val.substring(0, val.length() - 1) + replacement;
        BigDecimal bd = new BigDecimal(cleanVal);
        if (negative) {
            bd = bd.negate();
        }
        return bd.movePointLeft(scale);
    }

    private static long parseSignedLong(String val) {
        if (val == null || val.trim().isEmpty()) {
            return 0;
        }
        val = val.trim();
        char last = val.charAt(val.length() - 1);
        boolean negative = false;
        char replacement = last;
        if (last >= 'p' && last <= 'y') {
            negative = true;
            replacement = (char) ('0' + (last - 'p'));
        }
        String cleanVal = val.substring(0, val.length() - 1) + replacement;
        long l = Long.parseLong(cleanVal);
        return negative ? -l : l;
    }

    private static boolean checkSizeError(BigDecimal val, int digits, int scale, boolean signed) {
        if (val == null) return true;
        try {
            BigDecimal limit = BigDecimal.TEN.pow(digits - scale).subtract(BigDecimal.ONE.movePointLeft(scale));
            BigDecimal minLimit = signed ? limit.negate() : BigDecimal.ZERO;
            return val.compareTo(limit) > 0 || val.compareTo(minLimit) < 0;
        } catch (Exception e) {
            return true;
        }
    }

    private static boolean checkSizeError(long val, int digits, boolean signed) {
        long limit = java.math.BigInteger.TEN.pow(digits).subtract(java.math.BigInteger.ONE).longValueExact();
        long minLimit = signed ? -limit : 0;
        return val > limit || val < minLimit;
    }

    private static String padString(String val, int length) {
        if (val == null) val = "";
        String padded = String.format("%-" + length + "s", val);
        if (padded.length() > length) return padded.substring(0, length);
        return padded;
    }

    private static void writeBytes(byte[] b) {
        if (b != null) {
            System.out.write(b, 0, b.length);
        }
    }

}