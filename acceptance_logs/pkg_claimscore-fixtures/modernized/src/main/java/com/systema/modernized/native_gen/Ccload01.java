package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Ccload01 {

    public int return_code = 0;
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
    public String customer_record = "";
    public String cus_customer_id = "      ";
    public String cus_name = "                              ";
    public String cus_status = " ";
    public String cus_city = "                    ";
    public String cus_state = "  ";
    public String cus_risk_level = " ";
    public String cus_reserved = "                    ";
    public String ws_pol_status = "  ";
    public String ws_cus_status = "  ";
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

    private void populate_customer_record(String line) {
        if (line == null) line = "";
        customer_record = line;
        if (line.length() >= 6) {
            String val = line.substring(0, 6).trim();
            cus_customer_id = val;
        }
        if (line.length() >= 36) {
            String val = line.substring(6, 36).trim();
            cus_name = val;
        }
        if (line.length() >= 37) {
            String val = line.substring(36, 37).trim();
            cus_status = val;
        }
        if (line.length() >= 57) {
            String val = line.substring(37, 57).trim();
            cus_city = val;
        }
        if (line.length() >= 59) {
            String val = line.substring(57, 59).trim();
            cus_state = val;
        }
        if (line.length() >= 60) {
            String val = line.substring(59, 60).trim();
            cus_risk_level = val;
        }
        if (line.length() >= 80) {
            String val = line.substring(60, 80).trim();
            cus_reserved = val;
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

    private String resolve_path_customer_master() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("CUSTOMER-MASTER");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/work/customer.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "CUSTOMER-MASTER";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/work/customer.dat";
        }
        return resolvedPath;
    }

    private java.util.Map<String, String> customer_master_records = new java.util.LinkedHashMap<>();
    private java.util.Iterator<String> customer_master_iterator;

    private void save_customer_master() {
        try {
            java.nio.file.Path p = Paths.get(resolve_path_customer_master());
            if (p.getParent() != null) Files.createDirectories(p.getParent());
            try (BufferedWriter w = Files.newBufferedWriter(p)) {
                for (String line : customer_master_records.values()) {
                    w.write(line);
                    w.newLine();
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void open_customer_master() {
        try {
            customer_master_records.clear();
            java.nio.file.Path p = Paths.get(resolve_path_customer_master());
            if (Files.exists(p)) {
                try (BufferedReader r = Files.newBufferedReader(p)) {
                    String line;
                    while ((line = r.readLine()) != null) {
                        if (line.length() >= 6) {
                            String key = line.substring(0, 6).trim();
                            customer_master_records.put(key, line);
                        }
                    }
                }
            }
            customer_master_iterator = customer_master_records.values().iterator();
            ws_cus_status = "00";
        } catch (IOException e) {
            ws_cus_status = "35";
        }
    }

    private void populate_customer_master_fields(String line) {
        if (line.length() >= 6) {
            String val = line.substring(0, 6).trim();
            cus_customer_id = val;
        }
        if (line.length() >= 36) {
            String val = line.substring(6, 36).trim();
            cus_name = val;
        }
        if (line.length() >= 37) {
            String val = line.substring(36, 37).trim();
            cus_status = val;
        }
        if (line.length() >= 57) {
            String val = line.substring(37, 57).trim();
            cus_city = val;
        }
        if (line.length() >= 59) {
            String val = line.substring(57, 59).trim();
            cus_state = val;
        }
        if (line.length() >= 60) {
            String val = line.substring(59, 60).trim();
            cus_risk_level = val;
        }
        if (line.length() >= 80) {
            String val = line.substring(60, 80).trim();
            cus_reserved = val;
        }
    }

    private String format_customer_master_record() {
        return String.format("%-6s%-30s%-1s%-20s%-2s%-1s%-20s", cus_customer_id, cus_name, cus_status, cus_city, cus_state, cus_risk_level, cus_reserved);
    }

    private boolean read_customer_master() {
        if (customer_master_iterator == null) {
            customer_master_iterator = customer_master_records.values().iterator();
        }
        if (!customer_master_iterator.hasNext()) {
            ws_cus_status = "10";
            return false;
        }
        String line = customer_master_iterator.next();
        populate_customer_master_fields(line);
        ws_cus_status = "00";
        return true;
    }

    private boolean read_customer_master_key(String key) {
        String line = customer_master_records.get(key.trim());
        if (line == null) {
            ws_cus_status = "23";
            return false;
        }
        populate_customer_master_fields(line);
        ws_cus_status = "00";
        return true;
    }

    private boolean write_customer_master() {
        String line = format_customer_master_record();
        if (line.length() >= 6) {
            String key = line.substring(0, 6).trim();
            if (customer_master_records.containsKey(key)) {
                ws_cus_status = "22";
                return false;
            }
            customer_master_records.put(key, line);
            save_customer_master();
            ws_cus_status = "00";
            return true;
        }
        return false;
    }

    private boolean rewrite_customer_master() {
        String line = format_customer_master_record();
        if (line.length() >= 6) {
            String key = line.substring(0, 6).trim();
            if (!customer_master_records.containsKey(key)) {
                ws_cus_status = "23";
                return false;
            }
            customer_master_records.put(key, line);
            save_customer_master();
            ws_cus_status = "00";
            return true;
        }
        return false;
    }

    private boolean delete_customer_master() {
        String line = format_customer_master_record();
        if (line.length() >= 6) {
            String key = line.substring(0, 6).trim();
            if (!customer_master_records.containsKey(key)) {
                ws_cus_status = "23";
                return false;
            }
            customer_master_records.remove(key);
            save_customer_master();
            ws_cus_status = "00";
            return true;
        }
        return false;
    }

    private boolean delete_customer_master_key(String key) {
        if (key == null) return false;
        if (!customer_master_records.containsKey(key.trim())) {
            ws_cus_status = "23";
            return false;
        }
        customer_master_records.remove(key.trim());
        save_customer_master();
        ws_cus_status = "00";
        return true;
    }

    private boolean start_customer_master(String key, String op) {
        if (key == null) return false;
        java.util.Iterator<java.util.Map.Entry<String, String>> it = customer_master_records.entrySet().iterator();
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
            ws_cus_status = "23";
            return false;
        }
        // Reposition iterator so that the next read returns the found element
        customer_master_iterator = customer_master_records.values().iterator();
        for (int i = 0; i < skipCount; i++) {
            if (customer_master_iterator.hasNext()) customer_master_iterator.next();
        }
        ws_cus_status = "00";
        return true;
    }

    private void close_customer_master() {
        save_customer_master();
        customer_master_records.clear();
        customer_master_iterator = null;
        ws_cus_status = "00";
    }

    private boolean programExited = false;
    private int nextParagraphIndex = -1;
    private boolean skipToNextSentence = false;
    private final int total_paras = 3;

    public static class StopRunException extends RuntimeException {}

    private int getParagraphIndex(String name) {
        if (name == null) return -1;
        switch (name) {
            case "main_section": return 0;
            case "load_customers": return 1;
            case "load_policies": return 2;
            default: return -1;
        }
    }

    private void runParagraph(int idx) {
        if (programExited) return;
        switch (idx) {
            case 0: main_section(); break;
            case 1: load_customers(); break;
            case 2: load_policies(); break;
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
        while (i < 3) {
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
        if (!skipToNextSentence) {
            open_policy_master();
                    open_customer_master();
        }
        if (!skipToNextSentence) {
            perform("load_customers", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        if (!skipToNextSentence) {
            perform("load_policies", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        if (!skipToNextSentence) {
            close_policy_master();
                    close_customer_master();
        }
        if (!skipToNextSentence) { return_code = 0; }
        if (true) { programExited = true; return; }
    }

    private void load_customers() {
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            cus_customer_id = padString(String.valueOf(""), 6);
                    cus_name = padString(String.valueOf(""), 30);
                    cus_status = padString(String.valueOf(""), 1);
                    cus_city = padString(String.valueOf(""), 20);
                    cus_state = padString(String.valueOf(""), 2);
                    cus_risk_level = padString(String.valueOf(""), 1);
                    cus_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { cus_customer_id = padString(String.valueOf("U00001"), 6); }
        if (!skipToNextSentence) { cus_name = padString(String.valueOf("GLOBAL MOTORS INDIA"), 30); }
        if (!skipToNextSentence) { cus_status = padString(String.valueOf("A"), 1); }
        if (!skipToNextSentence) { cus_city = padString(String.valueOf("HYDERABAD"), 20); }
        if (!skipToNextSentence) { cus_state = padString(String.valueOf("TS"), 2); }
        if (!skipToNextSentence) { cus_risk_level = padString(String.valueOf("L"), 1); }
        if (!skipToNextSentence) { write_customer_master(); }
        if (!skipToNextSentence) {
            cus_customer_id = padString(String.valueOf(""), 6);
                    cus_name = padString(String.valueOf(""), 30);
                    cus_status = padString(String.valueOf(""), 1);
                    cus_city = padString(String.valueOf(""), 20);
                    cus_state = padString(String.valueOf(""), 2);
                    cus_risk_level = padString(String.valueOf(""), 1);
                    cus_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { cus_customer_id = padString(String.valueOf("U00002"), 6); }
        if (!skipToNextSentence) { cus_name = padString(String.valueOf("SUNRISE RETAIL GROUP"), 30); }
        if (!skipToNextSentence) { cus_status = padString(String.valueOf("A"), 1); }
        if (!skipToNextSentence) { cus_city = padString(String.valueOf("VIJAYAWADA"), 20); }
        if (!skipToNextSentence) { cus_state = padString(String.valueOf("AP"), 2); }
        if (!skipToNextSentence) { cus_risk_level = padString(String.valueOf("M"), 1); }
        if (!skipToNextSentence) { write_customer_master(); }
        if (!skipToNextSentence) {
            cus_customer_id = padString(String.valueOf(""), 6);
                    cus_name = padString(String.valueOf(""), 30);
                    cus_status = padString(String.valueOf(""), 1);
                    cus_city = padString(String.valueOf(""), 20);
                    cus_state = padString(String.valueOf(""), 2);
                    cus_risk_level = padString(String.valueOf(""), 1);
                    cus_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { cus_customer_id = padString(String.valueOf("U00003"), 6); }
        if (!skipToNextSentence) { cus_name = padString(String.valueOf("ORBIT TECHNOLOGIES"), 30); }
        if (!skipToNextSentence) { cus_status = padString(String.valueOf("A"), 1); }
        if (!skipToNextSentence) { cus_city = padString(String.valueOf("CHENNAI"), 20); }
        if (!skipToNextSentence) { cus_state = padString(String.valueOf("TN"), 2); }
        if (!skipToNextSentence) { cus_risk_level = padString(String.valueOf("H"), 1); }
        if (!skipToNextSentence) { write_customer_master(); }
    }

    private void load_policies() {
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            pol_policy_id = padString(String.valueOf(""), 10);
                    pol_customer_id = padString(String.valueOf(""), 6);
                    pol_type = padString(String.valueOf(""), 2);
                    pol_status = padString(String.valueOf(""), 1);
                    pol_currency = padString(String.valueOf(""), 3);
                    pol_cover_limit = BigDecimal.ZERO;
                    pol_deductible = BigDecimal.ZERO;
                    pol_effective_date = 0;
                    pol_expiry_date = 0;
                    pol_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { pol_policy_id = padString(String.valueOf("PL00000001"), 10); }
        if (!skipToNextSentence) { pol_customer_id = padString(String.valueOf("U00001"), 6); }
        if (!skipToNextSentence) { pol_type = padString(String.valueOf("MV"), 2); }
        if (!skipToNextSentence) { pol_status = padString(String.valueOf("A"), 1); }
        if (!skipToNextSentence) { pol_currency = padString(String.valueOf("INR"), 3); }
        if (!skipToNextSentence) { pol_cover_limit = new BigDecimal("500000.00"); }
        if (!skipToNextSentence) { pol_deductible = new BigDecimal("25000.00"); }
        if (!skipToNextSentence) { pol_effective_date = 20260101; }
        if (!skipToNextSentence) { pol_expiry_date = 20261231; }
        if (!skipToNextSentence) { write_policy_master(); }
        if (!skipToNextSentence) {
            pol_policy_id = padString(String.valueOf(""), 10);
                    pol_customer_id = padString(String.valueOf(""), 6);
                    pol_type = padString(String.valueOf(""), 2);
                    pol_status = padString(String.valueOf(""), 1);
                    pol_currency = padString(String.valueOf(""), 3);
                    pol_cover_limit = BigDecimal.ZERO;
                    pol_deductible = BigDecimal.ZERO;
                    pol_effective_date = 0;
                    pol_expiry_date = 0;
                    pol_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { pol_policy_id = padString(String.valueOf("PL00000002"), 10); }
        if (!skipToNextSentence) { pol_customer_id = padString(String.valueOf("U00002"), 6); }
        if (!skipToNextSentence) { pol_type = padString(String.valueOf("HE"), 2); }
        if (!skipToNextSentence) { pol_status = padString(String.valueOf("A"), 1); }
        if (!skipToNextSentence) { pol_currency = padString(String.valueOf("INR"), 3); }
        if (!skipToNextSentence) { pol_cover_limit = new BigDecimal("300000.00"); }
        if (!skipToNextSentence) { pol_deductible = new BigDecimal("10000.00"); }
        if (!skipToNextSentence) { pol_effective_date = 20260101; }
        if (!skipToNextSentence) { pol_expiry_date = 20261231; }
        if (!skipToNextSentence) { write_policy_master(); }
        if (!skipToNextSentence) {
            pol_policy_id = padString(String.valueOf(""), 10);
                    pol_customer_id = padString(String.valueOf(""), 6);
                    pol_type = padString(String.valueOf(""), 2);
                    pol_status = padString(String.valueOf(""), 1);
                    pol_currency = padString(String.valueOf(""), 3);
                    pol_cover_limit = BigDecimal.ZERO;
                    pol_deductible = BigDecimal.ZERO;
                    pol_effective_date = 0;
                    pol_expiry_date = 0;
                    pol_reserved = padString(String.valueOf(""), 20);
        }
        if (!skipToNextSentence) { pol_policy_id = padString(String.valueOf("PL00000003"), 10); }
        if (!skipToNextSentence) { pol_customer_id = padString(String.valueOf("U00003"), 6); }
        if (!skipToNextSentence) { pol_type = padString(String.valueOf("PR"), 2); }
        if (!skipToNextSentence) { pol_status = padString(String.valueOf("E"), 1); }
        if (!skipToNextSentence) { pol_currency = padString(String.valueOf("INR"), 3); }
        if (!skipToNextSentence) { pol_cover_limit = new BigDecimal("150000.00"); }
        if (!skipToNextSentence) { pol_deductible = new BigDecimal("15000.00"); }
        if (!skipToNextSentence) { pol_effective_date = 20250101; }
        if (!skipToNextSentence) { pol_expiry_date = 20251231; }
        if (!skipToNextSentence) { write_policy_master(); }
    }

    public static void main(String[] args) {
        try {
            new Ccload01().execute();
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