package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Idxmiss {

    public int return_code = 0;
    public String idx_rec = "";
    public String rec_key = "     ";
    public String rec_val = "                    ";
    public String ws_status = "  ";
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    public byte[] get_idx_rec_bytes() {
        byte[] c_0 = rec_key.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] c_1 = rec_val.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] res = new byte[c_0.length + c_1.length];
        System.arraycopy(c_0, 0, res, 0, c_0.length);
        System.arraycopy(c_1, 0, res, 0 + c_0.length, c_1.length);
        return res;
    }
    private void populate_idx_rec(String line) {
        if (line == null) line = "";
        idx_rec = line;
        if (line.length() >= 5) {
            String val = line.substring(0, 5).trim();
            rec_key = val;
        }
        if (line.length() >= 25) {
            String val = line.substring(5, 25).trim();
            rec_val = val;
        }
    }


    private String resolve_path_idx_file() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("IDX-FILE");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("/run/IDX.DAT");
        }
        if (resolvedPath == null) {
            String cleanLogical = "IDX-FILE";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "/run/IDX.DAT";
        }
        return resolvedPath;
    }

    private java.util.Map<String, String> idx_file_records = new java.util.LinkedHashMap<>();
    private java.util.List<String> idx_file_db_list = new java.util.ArrayList<>();
    private java.util.Iterator<String> idx_file_iterator;
    private boolean idx_file_eof = false;

    private void save_idx_file() {
        try {
            java.nio.file.Path p = Paths.get(resolve_path_idx_file());
            if (p.getParent() != null) Files.createDirectories(p.getParent());
            boolean hasDb = false;
            try {
                if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                    hasDb = true;
                }
            } catch (Throwable t) {}
            java.util.Collection<String> linesToWrite;
            if (hasDb) {
                linesToWrite = com.systema.modernized.SpringContextHelper.jdbcTemplate.query(
                    "SELECT record_col FROM idx_file_vsam ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col")
                );
            } else {
                linesToWrite = idx_file_records.values();
            }
            try (BufferedWriter w = Files.newBufferedWriter(p)) {
                for (String line : linesToWrite) {
                    w.write(line);
                    w.newLine();
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void open_idx_file() {
        open_idx_file("INPUT");
    }

    private void open_idx_file(String mode) {
        try {
            idx_file_records.clear();
            idx_file_db_list.clear();
            idx_file_iterator = null;
            idx_file_eof = false;
            boolean hasDb = false;
            try {
                if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                    hasDb = true;
                }
            } catch (Throwable t) {}
            java.nio.file.Path p = Paths.get(resolve_path_idx_file());
            if (hasDb) {
                com.systema.modernized.SpringContextHelper.jdbcTemplate.execute(
                    "CREATE TABLE IF NOT EXISTS idx_file_vsam (key_col VARCHAR(255) PRIMARY KEY, record_col VARCHAR(4000))"
                );
                if ("OUTPUT".equalsIgnoreCase(mode)) {
                    com.systema.modernized.SpringContextHelper.jdbcTemplate.execute("DELETE FROM idx_file_vsam");
                } else if (Files.exists(p)) {
                    try (BufferedReader r = Files.newBufferedReader(p)) {
                        String line;
                        int rrn = 1;
                        while ((line = r.readLine()) != null) {
                            String key = "";
                            if (line.length() >= 5) {
                                key = line.substring(0, 5).trim();
                            }
                            if (!key.isEmpty()) {
                                try {
                                    com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                                        "INSERT INTO idx_file_vsam (key_col, record_col) VALUES (?, ?)",
                                        key, line
                                    );
                                } catch (Exception e) {}
                            }
                        }
                    }
                }
            } else {
                if ("OUTPUT".equalsIgnoreCase(mode)) {
                    if (Files.exists(p)) Files.delete(p);
                } else if (Files.exists(p)) {
                    try (BufferedReader r = Files.newBufferedReader(p)) {
                        String line;
                        while ((line = r.readLine()) != null) {
                            if (line.length() >= 5) {
                                String key = line.substring(0, 5).trim();
                                idx_file_records.put(key, line);
                            }
                        }
                    }
                }
            }
            if (!hasDb) idx_file_iterator = idx_file_records.values().iterator();
            ws_status = "00";
        } catch (IOException e) {
            ws_status = "35";
        }
    }

    private void populate_idx_file_fields(String line) {
        if (line.length() >= 5) {
            String val = line.substring(0, 5);
            rec_key = val;
        }
        if (line.length() >= 25) {
            String val = line.substring(5, 25);
            rec_val = val;
        }
    }

    private String format_idx_file_record() {
        return String.format("%-5s%-20s", rec_key, rec_val);
    }

    private boolean read_idx_file() {
        if (idx_file_eof) {
            ws_status = "46";
            return false;
        }
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            if (idx_file_iterator == null) {
                idx_file_db_list = com.systema.modernized.SpringContextHelper.jdbcTemplate.query(
                    "SELECT record_col FROM idx_file_vsam ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col")
                );
                idx_file_iterator = idx_file_db_list.iterator();
            }
            if (!idx_file_iterator.hasNext()) {
                idx_file_eof = true;
                ws_status = "10";
                return false;
            }
            String line = idx_file_iterator.next();
            populate_idx_file_fields(line);
            ws_status = "00";
            return true;
        } else {
            if (idx_file_iterator == null) {
                idx_file_iterator = idx_file_records.values().iterator();
            }
            if (!idx_file_iterator.hasNext()) {
                idx_file_eof = true;
                ws_status = "10";
                return false;
            }
            String line = idx_file_iterator.next();
            populate_idx_file_fields(line);
            ws_status = "00";
            return true;
        }
    }

    private boolean read_idx_file_key(String key) {
        return read_idx_file_key(key, "REC-KEY");
    }

    private boolean read_idx_file_key(String key, String keyName) {
        idx_file_eof = false;
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String line = null;
            String queryKey = keyName.toUpperCase();
            try {
                boolean matched = false;
                if (!matched) {
                    try {
                        line = com.systema.modernized.SpringContextHelper.jdbcTemplate.queryForObject(
                            "SELECT record_col FROM idx_file_vsam WHERE key_col = ?",
                            String.class, key.trim()
                        );
                    } catch (Exception e) {
                        try {
                            String keyWithLeadingZero = key.trim();
                            try {
                                keyWithLeadingZero = String.valueOf(Integer.parseInt(keyWithLeadingZero));
                            } catch (Exception ex) {}
                            line = com.systema.modernized.SpringContextHelper.jdbcTemplate.queryForObject(
                                "SELECT record_col FROM idx_file_vsam WHERE key_col = ?",
                                String.class, keyWithLeadingZero
                            );
                        } catch (Exception ex) {}
                    }
                }
            } catch (Exception e) {}
            if (line == null) {
                ws_status = "23";
                return false;
            }
            populate_idx_file_fields(line);
            ws_status = "00";
            return true;
        } else {
            String queryKey = keyName.toUpperCase();
            String line = null;
            boolean matched = false;
            if (!matched) {
                line = idx_file_records.get(key.trim());
                if (line == null) {
                    String keyWithLeadingZero = key.trim();
                    try {
                        keyWithLeadingZero = String.valueOf(Integer.parseInt(keyWithLeadingZero));
                    } catch (Exception e) {}
                    line = idx_file_records.get(keyWithLeadingZero);
                }
            }
            if (line == null) {
                ws_status = "23";
                return false;
            }
            populate_idx_file_fields(line);
            ws_status = "00";
            return true;
        }
    }

    private boolean write_idx_file() {
        String line = format_idx_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            if (line.length() >= 5) {
                key = line.substring(0, 5).trim();
            }
            try {
                int existing = com.systema.modernized.SpringContextHelper.jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM idx_file_vsam WHERE key_col = ?", Integer.class, key
                );
                if (existing > 0) {
                    ws_status = "22";
                    return false;
                }
                com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                    "INSERT INTO idx_file_vsam (key_col, record_col) VALUES (?, ?)", key, line
                );
                save_idx_file();
                ws_status = "00";
                return true;
            } catch (Exception e) {
                ws_status = "22";
                return false;
            }
        } else {
            if (line.length() >= 5) {
                String key = line.substring(0, 5).trim();
                if (idx_file_records.containsKey(key)) {
                    ws_status = "22";
                    return false;
                }
                idx_file_records.put(key, line);
                save_idx_file();
                ws_status = "00";
                return true;
            }
            return false;
        }
    }

    private boolean rewrite_idx_file() {
        String line = format_idx_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            if (line.length() >= 5) {
                key = line.substring(0, 5).trim();
            }
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "UPDATE idx_file_vsam SET record_col = ? WHERE key_col = ?", line, key
            );
            if (rows == 0) {
                ws_status = "23";
                return false;
            }
            save_idx_file();
            ws_status = "00";
            return true;
        } else {
            if (line.length() >= 5) {
                String key = line.substring(0, 5).trim();
                if (!idx_file_records.containsKey(key)) {
                    ws_status = "23";
                    return false;
                }
                idx_file_records.put(key, line);
                save_idx_file();
                ws_status = "00";
                return true;
            }
            return false;
        }
    }

    private boolean delete_idx_file() {
        String line = format_idx_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            if (line.length() >= 5) {
                key = line.substring(0, 5).trim();
            }
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "DELETE FROM idx_file_vsam WHERE key_col = ?", key
            );
            if (rows == 0) {
                ws_status = "23";
                return false;
            }
            save_idx_file();
            ws_status = "00";
            return true;
        } else {
            if (line.length() >= 5) {
                String key = line.substring(0, 5).trim();
                if (!idx_file_records.containsKey(key)) {
                    ws_status = "23";
                    return false;
                }
                idx_file_records.remove(key);
                save_idx_file();
                ws_status = "00";
                return true;
            }
            return false;
        }
    }

    private boolean delete_idx_file_key(String key) {
        if (key == null) return false;
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "DELETE FROM idx_file_vsam WHERE key_col = ?", key.trim()
            );
            if (rows == 0) {
                ws_status = "23";
                return false;
            }
            save_idx_file();
            ws_status = "00";
            return true;
        } else {
            if (!idx_file_records.containsKey(key.trim())) {
                ws_status = "23";
                return false;
            }
            idx_file_records.remove(key.trim());
            save_idx_file();
            ws_status = "00";
            return true;
        }
    }

    private boolean start_idx_file(String key, String op) {
        return start_idx_file(key, op, "REC-KEY");
    }

    private boolean start_idx_file(String key, String op, String keyName) {
        if (key == null) return false;
        idx_file_eof = false;
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String op_sql = op.trim();
            if (op_sql.equals("NOT <")) op_sql = ">=";
            String queryKey = keyName.toUpperCase();
            boolean matched = false;
            if (!matched) {
                idx_file_db_list = com.systema.modernized.SpringContextHelper.jdbcTemplate.query(
                    "SELECT record_col FROM idx_file_vsam WHERE key_col " + op_sql + " ? ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col"), key.trim()
                );
            }
            if (idx_file_db_list.isEmpty()) {
                ws_status = "23";
                return false;
            }
            idx_file_iterator = idx_file_db_list.iterator();
            ws_status = "00";
            return true;
        } else {
            String queryKey = keyName.toUpperCase();
            java.util.List<String> sortedRecords = new java.util.ArrayList<>(idx_file_records.values());
            boolean matched = false;
            if (!matched) {
                sortedRecords.sort((r1, r2) -> {
                    String v1 = r1.length() >= 5 ? r1.substring(0, 5) : "";
                    String v2 = r2.length() >= 5 ? r2.substring(0, 5) : "";
                    return v1.compareTo(v2);
                });
            }
            int skipCount = 0;
            boolean found = false;
            String targetKey = key.trim();
            for (String record : sortedRecords) {
                String val = "";
                boolean isAlt = false;
                if (!isAlt) {
                    if (record.length() >= 5) val = record.substring(0, 5).trim();
                }
                int cmp = val.compareTo(targetKey);
                boolean match = false;
                String startOp = op.trim();
                if (startOp.equals("=")) match = (cmp == 0);
                else if (startOp.equals(">")) match = (cmp > 0);
                else if (startOp.equals(">=") || startOp.equals("NOT <")) match = (cmp >= 0);
                if (match) {
                    found = true;
                    break;
                }
                skipCount++;
            }
            if (!found) {
                ws_status = "23";
                return false;
            }
            idx_file_iterator = sortedRecords.iterator();
            for (int i = 0; i < skipCount; i++) {
                if (idx_file_iterator.hasNext()) idx_file_iterator.next();
            }
            ws_status = "00";
            return true;
        }
    }

    private void close_idx_file() {
        save_idx_file();
        idx_file_records.clear();
        idx_file_db_list.clear();
        idx_file_iterator = null;
        ws_status = "00";
    }

    private boolean programExited = false;
    private int nextParagraphIndex = -1;
    private boolean skipToNextSentence = false;
    private final int total_paras = 1;

    public static class StopRunException extends RuntimeException {}

    private int getParagraphIndex(String name) {
        if (name == null) return -1;
        switch (name) {
            case "main_process": return 0;
            default: return -1;
        }
    }

    private void runParagraph(int idx) {
        if (programExited) return;
        switch (idx) {
            case 0: main_process(); break;
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

    private void main_process() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { open_idx_file("OUTPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { rec_key = padString(String.valueOf("KEY01"), 5); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { rec_val = padString(String.valueOf("VALUE ONE"), 20); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { write_idx_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_idx_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { open_idx_file("INPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { rec_key = padString(String.valueOf("NOKEY"), 5); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { read_idx_file_key(String.valueOf(rec_key), "REC-KEY"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            {
                    writeBytes(ws_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_idx_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { if (true) { programExited = true; return; } }
    }

    public static void main(String[] args) {
        try {
            new Idxmiss().execute();
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