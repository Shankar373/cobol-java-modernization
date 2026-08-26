package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Ccproc01 {

    public int return_code = 0;
    public String claim_line = "                                                                                                                                                        ";
    public String policy_record = "";
    public String pol_policy_id = "          ";
    public String pol_customer_id = "      ";
    public String pol_type = "  ";
    public String pol_status = " ";
    public String pol_currency = "   ";
    public BigDecimal pol_cover_limit = BigDecimal.ZERO;
    public BigDecimal pol_deductible = BigDecimal.ZERO;
    public int pol_effective_date = 0;
    public int pol_expiry_date = 0;
    public String pol_reserved = "                    ";
    public String audit_line = "                                                                                                                                                                                                                            ";
    public String exception_line = "                                                                                                                                                                                                                            ";
    public String claim_record = "";
    public String clm_id = "            ";
    public int clm_date = 0;
    public int clm_time = 0;
    public String clm_policy_id = "          ";
    public String clm_type = "  ";
    public String clm_channel = "  ";
    public BigDecimal clm_loss_amount = BigDecimal.ZERO;
    public String clm_description = "                                        ";
    public String clm_reported_by = "                    ";
    public String clm_reserved = "          ";
    public String ws_in_status = "  ";
    public String ws_pol_status = "  ";
    public String ws_eof = "N";
    public String ws_result = " ";
    public String ws_error_code = "    ";
    public String ws_error_text = "                                                                                ";
    public BigDecimal ws_approved_amount = BigDecimal.ZERO;
    public int ws_claim_count = 0;
    public int ws_approved_count = 0;
    public int ws_rejected_count = 0;
    public int ws_review_count = 0;
    public String ws_raw = "";
    public String raw_id = "            ";
    public String raw_date = "        ";
    public String raw_time = "      ";
    public String raw_policy = "          ";
    public String raw_type = "  ";
    public String raw_channel = "  ";
    public String raw_amount = "            ";
    public String raw_desc = "                                        ";
    public String raw_reporter = "                    ";
    public String raw_filler = "                                        ";
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    private void populate_policy_record(String line) {
        if (line == null) line = "";
        policy_record = line;
        if (line.length() >= 10) {
            String val = line.substring(0, 10).trim();
            pol_policy_id = val;
        }
        if (line.length() >= 16) {
            String val = line.substring(10, 16).trim();
            pol_customer_id = val;
        }
        if (line.length() >= 18) {
            String val = line.substring(16, 18).trim();
            pol_type = val;
        }
        if (line.length() >= 19) {
            String val = line.substring(18, 19).trim();
            pol_status = val;
        }
        if (line.length() >= 22) {
            String val = line.substring(19, 22).trim();
            pol_currency = val;
        }
        if (line.length() >= 35) {
            String val = line.substring(22, 35).trim();
            pol_cover_limit = parseSigned(val, 2);
        }
        if (line.length() >= 46) {
            String val = line.substring(35, 46).trim();
            pol_deductible = parseSigned(val, 2);
        }
        if (line.length() >= 54) {
            String val = line.substring(46, 54).trim();
            pol_effective_date = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 62) {
            String val = line.substring(54, 62).trim();
            pol_expiry_date = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 82) {
            String val = line.substring(62, 82).trim();
            pol_reserved = val;
        }
    }

    private void populate_claim_record(String line) {
        if (line == null) line = "";
        claim_record = line;
        if (line.length() >= 12) {
            String val = line.substring(0, 12).trim();
            clm_id = val;
        }
        if (line.length() >= 20) {
            String val = line.substring(12, 20).trim();
            clm_date = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 26) {
            String val = line.substring(20, 26).trim();
            clm_time = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 36) {
            String val = line.substring(26, 36).trim();
            clm_policy_id = val;
        }
        if (line.length() >= 38) {
            String val = line.substring(36, 38).trim();
            clm_type = val;
        }
        if (line.length() >= 40) {
            String val = line.substring(38, 40).trim();
            clm_channel = val;
        }
        if (line.length() >= 51) {
            String val = line.substring(40, 51).trim();
            clm_loss_amount = val.isEmpty() ? BigDecimal.ZERO : new BigDecimal(val).movePointLeft(2);
        }
        if (line.length() >= 91) {
            String val = line.substring(51, 91).trim();
            clm_description = val;
        }
        if (line.length() >= 111) {
            String val = line.substring(91, 111).trim();
            clm_reported_by = val;
        }
        if (line.length() >= 121) {
            String val = line.substring(111, 121).trim();
            clm_reserved = val;
        }
    }

    private void populate_ws_raw(String line) {
        if (line == null) line = "";
        ws_raw = line;
        if (line.length() >= 12) {
            String val = line.substring(0, 12).trim();
            raw_id = val;
        }
        if (line.length() >= 20) {
            String val = line.substring(12, 20).trim();
            raw_date = val;
        }
        if (line.length() >= 26) {
            String val = line.substring(20, 26).trim();
            raw_time = val;
        }
        if (line.length() >= 36) {
            String val = line.substring(26, 36).trim();
            raw_policy = val;
        }
        if (line.length() >= 38) {
            String val = line.substring(36, 38).trim();
            raw_type = val;
        }
        if (line.length() >= 40) {
            String val = line.substring(38, 40).trim();
            raw_channel = val;
        }
        if (line.length() >= 52) {
            String val = line.substring(40, 52).trim();
            raw_amount = val;
        }
        if (line.length() >= 92) {
            String val = line.substring(52, 92).trim();
            raw_desc = val;
        }
        if (line.length() >= 112) {
            String val = line.substring(92, 112).trim();
            raw_reporter = val;
        }
        if (line.length() >= 152) {
            String val = line.substring(112, 152).trim();
            raw_filler = val;
        }
    }


    private String resolve_path_claim_in() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("CLAIM-IN");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/in/claims.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "CLAIM-IN";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/in/claims.dat";
        }
        return resolvedPath;
    }

    private BufferedReader claim_in_reader;
    private void open_claim_in() {
        try {
            claim_in_reader = Files.newBufferedReader(Paths.get(resolve_path_claim_in()));
            ws_in_status = "00";
        } catch (IOException e) {
            ws_in_status = "35";
        }
    }

    private boolean read_claim_in() {
        try {
            String line = claim_in_reader.readLine();
            if (line == null) {
                ws_in_status = "10";
                return false;
            } else {
                String val_claim_line = (line.length() >= 152) ? line.substring(0, 152).trim() : (line.length() > 0 ? line.substring(0).trim() : "");
                claim_line = val_claim_line;
                ws_in_status = "00";
            }
            return true;
        } catch (IOException e) {
            ws_in_status = "30";
            return false;
        }
    }

    private void close_claim_in() {
        try {
            if (claim_in_reader != null) claim_in_reader.close();
            ws_in_status = "00";
        } catch (IOException e) {
            ws_in_status = "30";
        }
    }

    private String resolve_path_policy_master() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("POLICY-MASTER");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/work/policy.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "POLICY-MASTER";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/work/policy.dat";
        }
        return resolvedPath;
    }

    private java.util.Map<String, String> policy_master_records = new java.util.LinkedHashMap<>();
    private java.util.Iterator<String> policy_master_iterator;

    private void save_policy_master() {
        try {
            java.nio.file.Path p = Paths.get(resolve_path_policy_master());
            if (p.getParent() != null) Files.createDirectories(p.getParent());
            try (BufferedWriter w = Files.newBufferedWriter(p)) {
                for (String line : policy_master_records.values()) {
                    w.write(line);
                    w.newLine();
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void open_policy_master() {
        try {
            policy_master_records.clear();
            java.nio.file.Path p = Paths.get(resolve_path_policy_master());
            if (Files.exists(p)) {
                try (BufferedReader r = Files.newBufferedReader(p)) {
                    String line;
                    while ((line = r.readLine()) != null) {
                        if (line.length() >= 10) {
                            String key = line.substring(0, 10).trim();
                            policy_master_records.put(key, line);
                        }
                    }
                }
            }
            policy_master_iterator = policy_master_records.values().iterator();
            ws_pol_status = "00";
        } catch (IOException e) {
            ws_pol_status = "35";
        }
    }

    private void populate_policy_master_fields(String line) {
        if (line.length() >= 10) {
            String val = line.substring(0, 10).trim();
            pol_policy_id = val;
        }
        if (line.length() >= 16) {
            String val = line.substring(10, 16).trim();
            pol_customer_id = val;
        }
        if (line.length() >= 18) {
            String val = line.substring(16, 18).trim();
            pol_type = val;
        }
        if (line.length() >= 19) {
            String val = line.substring(18, 19).trim();
            pol_status = val;
        }
        if (line.length() >= 22) {
            String val = line.substring(19, 22).trim();
            pol_currency = val;
        }
        if (line.length() >= 35) {
            String val = line.substring(22, 35).trim();
            pol_cover_limit = parseSigned(val, 2);
        }
        if (line.length() >= 46) {
            String val = line.substring(35, 46).trim();
            pol_deductible = parseSigned(val, 2);
        }
        if (line.length() >= 54) {
            String val = line.substring(46, 54).trim();
            pol_effective_date = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 62) {
            String val = line.substring(54, 62).trim();
            pol_expiry_date = val.isEmpty() ? 0 : Integer.parseInt(val);
        }
        if (line.length() >= 82) {
            String val = line.substring(62, 82).trim();
            pol_reserved = val;
        }
    }

    private String format_policy_master_record() {
        return String.format("%-10s%-6s%-2s%-1s%-3s%013d%011d%08d%08d%-20s", pol_policy_id, pol_customer_id, pol_type, pol_status, pol_currency, (pol_cover_limit.movePointRight(2).longValue()), (pol_deductible.movePointRight(2).longValue()), pol_effective_date, pol_expiry_date, pol_reserved);
    }

    private boolean read_policy_master() {
        if (policy_master_iterator == null) {
            policy_master_iterator = policy_master_records.values().iterator();
        }
        if (!policy_master_iterator.hasNext()) {
            ws_pol_status = "10";
            return false;
        }
        String line = policy_master_iterator.next();
        populate_policy_master_fields(line);
        ws_pol_status = "00";
        return true;
    }

    private boolean read_policy_master_key(String key) {
        String line = policy_master_records.get(key.trim());
        if (line == null) {
            ws_pol_status = "23";
            return false;
        }
        populate_policy_master_fields(line);
        ws_pol_status = "00";
        return true;
    }

    private boolean write_policy_master() {
        String line = format_policy_master_record();
        if (line.length() >= 10) {
            String key = line.substring(0, 10).trim();
            if (policy_master_records.containsKey(key)) {
                ws_pol_status = "22";
                return false;
            }
            policy_master_records.put(key, line);
            save_policy_master();
            ws_pol_status = "00";
            return true;
        }
        return false;
    }

    private boolean rewrite_policy_master() {
        String line = format_policy_master_record();
        if (line.length() >= 10) {
            String key = line.substring(0, 10).trim();
            if (!policy_master_records.containsKey(key)) {
                ws_pol_status = "23";
                return false;
            }
            policy_master_records.put(key, line);
            save_policy_master();
            ws_pol_status = "00";
            return true;
        }
        return false;
    }

    private boolean delete_policy_master() {
        String line = format_policy_master_record();
        if (line.length() >= 10) {
            String key = line.substring(0, 10).trim();
            if (!policy_master_records.containsKey(key)) {
                ws_pol_status = "23";
                return false;
            }
            policy_master_records.remove(key);
            save_policy_master();
            ws_pol_status = "00";
            return true;
        }
        return false;
    }

    private boolean delete_policy_master_key(String key) {
        if (key == null) return false;
        if (!policy_master_records.containsKey(key.trim())) {
            ws_pol_status = "23";
            return false;
        }
        policy_master_records.remove(key.trim());
        save_policy_master();
        ws_pol_status = "00";
        return true;
    }

    private boolean start_policy_master(String key, String op) {
        if (key == null) return false;
        java.util.Iterator<java.util.Map.Entry<String, String>> it = policy_master_records.entrySet().iterator();
        int skipCount = 0;
        boolean found = false;
        String targetKey = key.trim();
        while (it.hasNext()) {
            java.util.Map.Entry<String, String> entry = it.next();
            String k = entry.getKey();
            int cmp = k.compareTo(targetKey);
            boolean match = false;
            if (op.equals("=")) match = (cmp == 0);
            else if (op.equals(">")) match = (cmp > 0);
            else if (op.equals(">=")) match = (cmp >= 0);
            if (match) {
                found = true;
                break;
            }
            skipCount++;
        }
        if (!found) {
            ws_pol_status = "23";
            return false;
        }
        // Reposition iterator so that the next read returns the found element
        policy_master_iterator = policy_master_records.values().iterator();
        for (int i = 0; i < skipCount; i++) {
            if (policy_master_iterator.hasNext()) policy_master_iterator.next();
        }
        ws_pol_status = "00";
        return true;
    }

    private void close_policy_master() {
        save_policy_master();
        policy_master_records.clear();
        policy_master_iterator = null;
        ws_pol_status = "00";
    }

    private String resolve_path_audit_out() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("AUDIT-OUT");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/out/claim-audit.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "AUDIT-OUT";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/out/claim-audit.dat";
        }
        return resolvedPath;
    }

    private BufferedWriter audit_out_writer;
    private void open_audit_out() {
        try {
            java.nio.file.Path parent = Paths.get(resolve_path_audit_out()).getParent();
            if (parent != null) Files.createDirectories(parent);
            audit_out_writer = Files.newBufferedWriter(Paths.get(resolve_path_audit_out()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void write_audit_out() {
        try {
            audit_out_writer.write(String.format("%-220s", audit_line));
            audit_out_writer.newLine();
        } catch (IOException e) {
        }
    }

    private void close_audit_out() {
        try {
            if (audit_out_writer != null) audit_out_writer.close();
        } catch (IOException e) {
        }
    }

    private String resolve_path_exception_out() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("EXCEPTION-OUT");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/out/claim-exceptions.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "EXCEPTION-OUT";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/out/claim-exceptions.dat";
        }
        return resolvedPath;
    }

    private BufferedWriter exception_out_writer;
    private void open_exception_out() {
        try {
            java.nio.file.Path parent = Paths.get(resolve_path_exception_out()).getParent();
            if (parent != null) Files.createDirectories(parent);
            exception_out_writer = Files.newBufferedWriter(Paths.get(resolve_path_exception_out()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void write_exception_out() {
        try {
            exception_out_writer.write(String.format("%-220s", exception_line));
            exception_out_writer.newLine();
        } catch (IOException e) {
        }
    }

    private void close_exception_out() {
        try {
            if (exception_out_writer != null) exception_out_writer.close();
        } catch (IOException e) {
        }
    }

    private boolean programExited = false;
    private int nextParagraphIndex = -1;
    private boolean skipToNextSentence = false;
    private final int total_paras = 7;

    public static class StopRunException extends RuntimeException {}

    private int getParagraphIndex(String name) {
        if (name == null) return -1;
        switch (name) {
            case "main_section": return 0;
            case "map_claim": return 1;
            case "process_claim": return 2;
            case "validate_policy": return 3;
            case "calculate_settlement": return 4;
            case "write_audit": return 5;
            case "write_rejection": return 6;
            default: return -1;
        }
    }

    private void runParagraph(int idx) {
        if (programExited) return;
        switch (idx) {
            case 0: main_section(); break;
            case 1: map_claim(); break;
            case 2: process_claim(); break;
            case 3: validate_policy(); break;
            case 4: calculate_settlement(); break;
            case 5: write_audit(); break;
            case 6: write_rejection(); break;
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
        while (i < 7) {
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

    private void main_section() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { open_claim_in(); }
        if (!skipToNextSentence) { open_policy_master(); }
        if (!skipToNextSentence) {
            open_audit_out();
                    open_exception_out();
        }
        while (!(ws_eof.equals("Y"))) {
        if (skipToNextSentence) break;
        if (!read_claim_in()) {
            if (!skipToNextSentence) { ws_eof = padString(String.valueOf("Y"), 1); }
        } else {
            if (!skipToNextSentence) {
            perform("map_claim", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
            if (!skipToNextSentence) {
            perform("process_claim", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        }
        }
        if (!skipToNextSentence) {
            close_claim_in();
                    close_policy_master();
                    close_audit_out();
                    close_exception_out();
        }
        if (!skipToNextSentence) { System.out.println("CLAIMS PROCESSED: " + " " + String.format("%07d", ws_claim_count)); }
        if (!skipToNextSentence) { return_code = 0; }
        if (true) { programExited = true; return; }
    }

    private void map_claim() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { populate_ws_raw(claim_line); }
        if (!skipToNextSentence) { clm_id = padString(String.valueOf(raw_id), 12); }
        if (!skipToNextSentence) { clm_date = (raw_date == null || raw_date.trim().isEmpty()) ? 0 : Integer.parseInt(raw_date.trim()); }
        if (!skipToNextSentence) { clm_time = (raw_time == null || raw_time.trim().isEmpty()) ? 0 : Integer.parseInt(raw_time.trim()); }
        if (!skipToNextSentence) { clm_policy_id = padString(String.valueOf(raw_policy), 10); }
        if (!skipToNextSentence) { clm_type = padString(String.valueOf(raw_type), 2); }
        if (!skipToNextSentence) { clm_channel = padString(String.valueOf(raw_channel), 2); }
        if (!skipToNextSentence) { clm_loss_amount = (raw_amount == null || raw_amount.trim().isEmpty()) ? BigDecimal.ZERO : (raw_amount.trim().contains(".")) ? new BigDecimal(raw_amount.trim()) : new BigDecimal(raw_amount.trim()).movePointLeft(2); }
        if (!skipToNextSentence) { clm_description = padString(String.valueOf(raw_desc), 40); }
        if (!skipToNextSentence) { clm_reported_by = padString(String.valueOf(raw_reporter), 20); }
        if (!skipToNextSentence) { ws_claim_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_claim_count + 1)), 7, 0, false).intValue(); }
    }

    private void process_claim() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_result = padString(String.valueOf("V"), 1); }
        if (!skipToNextSentence) {
            ws_error_code = padString(String.valueOf(""), 4);
                    ws_error_text = padString(String.valueOf(""), 80);
        }
        if (!skipToNextSentence) { pol_policy_id = padString(String.valueOf(clm_policy_id), 10); }
        if (!skipToNextSentence) { read_policy_master_key(pol_policy_id); }
        if (!ws_pol_status.equals("00")) {
        if (!skipToNextSentence) { ws_result = padString(String.valueOf("I"), 1); }
        if (!skipToNextSentence) { ws_error_code = padString(String.valueOf("P001"), 4); }
        if (!skipToNextSentence) { ws_error_text = padString(String.valueOf("POLICY NOT FOUND"), 80); }
        } else {
        if (!skipToNextSentence) {
            perform("validate_policy", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        }
        if (ws_result.equals("V")) {
        if (!skipToNextSentence) {
            perform("calculate_settlement", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        }
        if (ws_result.equals("V") || ws_result.equals("M")) {
        if (!skipToNextSentence) {
            perform("write_audit", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        } else {
        if (!skipToNextSentence) {
            perform("write_rejection", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        }
    }

    private void validate_policy() {
        skipToNextSentence = false;
        if (!pol_status.equals("A")) {
        if (!skipToNextSentence) { ws_result = padString(String.valueOf("I"), 1); }
        if (!skipToNextSentence) { ws_error_code = padString(String.valueOf("P002"), 4); }
        if (!skipToNextSentence) { ws_error_text = padString(String.valueOf("POLICY INACTIVE OR EXPIRED"), 80); }
        } else if (!clm_type.equals(pol_type)) {
        if (!skipToNextSentence) { ws_result = padString(String.valueOf("I"), 1); }
        if (!skipToNextSentence) { ws_error_code = padString(String.valueOf("P003"), 4); }
        if (!skipToNextSentence) { ws_error_text = padString(String.valueOf("CLAIM TYPE NOT COVERED BY POLICY"), 80); }
        } else {
        if (!skipToNextSentence) { ; }
        }
    }

    private void calculate_settlement() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_approved_amount = com.systema.modernized.CobolFormatHelper.truncateToPic(clm_loss_amount.subtract(pol_deductible), 13, 2, true); }
        if (ws_approved_amount.compareTo(new BigDecimal("0")) < 0) {
        if (!skipToNextSentence) { ws_approved_amount = new BigDecimal("0"); }
        }
        if (ws_approved_amount.compareTo(pol_cover_limit) > 0) {
        if (!skipToNextSentence) { ws_approved_amount = pol_cover_limit; }
        }
        if (ws_approved_amount.compareTo(new BigDecimal("200000")) > 0) {
        if (!skipToNextSentence) { ws_result = padString(String.valueOf("M"), 1); }
        }
    }

    private void write_audit() {
        skipToNextSentence = false;
        if (ws_result.equals("M")) {
        if (!skipToNextSentence) { audit_line = padString(String.valueOf(clm_id + "|" + clm_policy_id + "|MANUAL_REVIEW|" + String.valueOf(ws_approved_amount) + "|" + clm_description), 220); }
        if (!skipToNextSentence) { write_audit_out(); }
        if (!skipToNextSentence) { ws_review_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_review_count + 1)), 7, 0, false).intValue(); }
        } else {
        if (!skipToNextSentence) { audit_line = padString(String.valueOf(clm_id + "|" + clm_policy_id + "|APPROVED|" + String.valueOf(ws_approved_amount) + "|" + clm_description), 220); }
        if (!skipToNextSentence) { write_audit_out(); }
        if (!skipToNextSentence) { ws_approved_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_approved_count + 1)), 7, 0, false).intValue(); }
        }
    }

    private void write_rejection() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rejected_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_rejected_count + 1)), 7, 0, false).intValue(); }
        if (!skipToNextSentence) { exception_line = padString(String.valueOf(clm_id + "|" + clm_policy_id + "|" + ws_error_code + "|" + ws_error_text + "|" + clm_description), 220); }
        if (!skipToNextSentence) { write_exception_out(); }
    }

    public static void main(String[] args) {
        try {
            new Ccproc01().execute();
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

    private static String padString(String val, int length) {
        if (val == null) val = "";
        String padded = String.format("%-" + length + "s", val);
        if (padded.length() > length) return padded.substring(0, length);
        return padded;
    }

}