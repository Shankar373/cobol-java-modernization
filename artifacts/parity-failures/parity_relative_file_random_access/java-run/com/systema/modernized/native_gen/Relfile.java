package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Relfile {

    public int return_code = 0;
    public String rel_rec = "";
    public String r_data = "                    ";
    public int ws_rrn = 0;
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    public byte[] get_rel_rec_bytes() {
        byte[] c_0 = r_data.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] res = new byte[c_0.length];
        System.arraycopy(c_0, 0, res, 0, c_0.length);
        return res;
    }
    private void populate_rel_rec(String line) {
        if (line == null) line = "";
        rel_rec = line;
        if (line.length() >= 20) {
            String val = line.substring(0, 20).trim();
            r_data = val;
        }
    }


    private String resolve_path_rel_file() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("REL-FILE");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("/run/REL.DAT");
        }
        if (resolvedPath == null) {
            String cleanLogical = "REL-FILE";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "/run/REL.DAT";
        }
        return resolvedPath;
    }

    private java.util.Map<String, String> rel_file_records = new java.util.LinkedHashMap<>();
    private java.util.List<String> rel_file_db_list = new java.util.ArrayList<>();
    private java.util.Iterator<String> rel_file_iterator;
    private boolean rel_file_eof = false;

    private void save_rel_file() {
        try {
            java.nio.file.Path p = Paths.get(resolve_path_rel_file());
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
                    "SELECT record_col FROM rel_file_vsam ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col")
                );
            } else {
                linesToWrite = rel_file_records.values();
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

    private void open_rel_file() {
        open_rel_file("INPUT");
    }

    private void open_rel_file(String mode) {
        try {
            rel_file_records.clear();
            rel_file_db_list.clear();
            rel_file_iterator = null;
            rel_file_eof = false;
            boolean hasDb = false;
            try {
                if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                    hasDb = true;
                }
            } catch (Throwable t) {}
            java.nio.file.Path p = Paths.get(resolve_path_rel_file());
            if (hasDb) {
                com.systema.modernized.SpringContextHelper.jdbcTemplate.execute(
                    "CREATE TABLE IF NOT EXISTS rel_file_vsam (key_col VARCHAR(255) PRIMARY KEY, record_col VARCHAR(4000))"
                );
                if ("OUTPUT".equalsIgnoreCase(mode)) {
                    com.systema.modernized.SpringContextHelper.jdbcTemplate.execute("DELETE FROM rel_file_vsam");
                } else if (Files.exists(p)) {
                    try (BufferedReader r = Files.newBufferedReader(p)) {
                        String line;
                        int rrn = 1;
                        while ((line = r.readLine()) != null) {
                            String key = "";
                            key = String.valueOf(rrn++);
                            if (!key.isEmpty()) {
                                try {
                                    com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                                        "INSERT INTO rel_file_vsam (key_col, record_col) VALUES (?, ?)",
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
                        int rrn = 1;
                        while ((line = r.readLine()) != null) {
                            rel_file_records.put(String.valueOf(rrn++), line);
                        }
                    }
                }
            }
            if (!hasDb) rel_file_iterator = rel_file_records.values().iterator();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void populate_rel_file_fields(String line) {
        if (line.length() >= 20) {
            String val = line.substring(0, 20);
            r_data = val;
        }
    }

    private String format_rel_file_record() {
        return String.format("%-20s", r_data);
    }

    private boolean read_rel_file() {
        if (rel_file_eof) {
            return false;
        }
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            if (rel_file_iterator == null) {
                rel_file_db_list = com.systema.modernized.SpringContextHelper.jdbcTemplate.query(
                    "SELECT record_col FROM rel_file_vsam ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col")
                );
                rel_file_iterator = rel_file_db_list.iterator();
            }
            if (!rel_file_iterator.hasNext()) {
                rel_file_eof = true;
                return false;
            }
            String line = rel_file_iterator.next();
            populate_rel_file_fields(line);
            return true;
        } else {
            if (rel_file_iterator == null) {
                rel_file_iterator = rel_file_records.values().iterator();
            }
            if (!rel_file_iterator.hasNext()) {
                rel_file_eof = true;
                return false;
            }
            String line = rel_file_iterator.next();
            populate_rel_file_fields(line);
            return true;
        }
    }

    private boolean read_rel_file_key(String key) {
        return read_rel_file_key(key, "WS-RRN");
    }

    private boolean read_rel_file_key(String key, String keyName) {
        rel_file_eof = false;
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
                            "SELECT record_col FROM rel_file_vsam WHERE key_col = ?",
                            String.class, key.trim()
                        );
                    } catch (Exception e) {
                        try {
                            String keyWithLeadingZero = key.trim();
                            try {
                                keyWithLeadingZero = String.valueOf(Integer.parseInt(keyWithLeadingZero));
                            } catch (Exception ex) {}
                            line = com.systema.modernized.SpringContextHelper.jdbcTemplate.queryForObject(
                                "SELECT record_col FROM rel_file_vsam WHERE key_col = ?",
                                String.class, keyWithLeadingZero
                            );
                        } catch (Exception ex) {}
                    }
                }
            } catch (Exception e) {}
            if (line == null) {
                return false;
            }
            populate_rel_file_fields(line);
            return true;
        } else {
            String queryKey = keyName.toUpperCase();
            String line = null;
            boolean matched = false;
            if (!matched) {
                line = rel_file_records.get(key.trim());
                if (line == null) {
                    String keyWithLeadingZero = key.trim();
                    try {
                        keyWithLeadingZero = String.valueOf(Integer.parseInt(keyWithLeadingZero));
                    } catch (Exception e) {}
                    line = rel_file_records.get(keyWithLeadingZero);
                }
            }
            if (line == null) {
                return false;
            }
            populate_rel_file_fields(line);
            return true;
        }
    }

    private boolean write_rel_file() {
        String line = format_rel_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            key = String.valueOf(ws_rrn).trim();
            try {
                int existing = com.systema.modernized.SpringContextHelper.jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM rel_file_vsam WHERE key_col = ?", Integer.class, key
                );
                if (existing > 0) {
                    return false;
                }
                com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                    "INSERT INTO rel_file_vsam (key_col, record_col) VALUES (?, ?)", key, line
                );
                save_rel_file();
                return true;
            } catch (Exception e) {
                return false;
            }
        } else {
            String key = String.valueOf(ws_rrn).trim();
            if (rel_file_records.containsKey(key)) {
                return false;
            }
            rel_file_records.put(key, line);
            save_rel_file();
            return true;
        }
    }

    private boolean rewrite_rel_file() {
        String line = format_rel_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            key = String.valueOf(ws_rrn).trim();
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "UPDATE rel_file_vsam SET record_col = ? WHERE key_col = ?", line, key
            );
            if (rows == 0) {
                return false;
            }
            save_rel_file();
            return true;
        } else {
            String key = String.valueOf(ws_rrn).trim();
            if (!rel_file_records.containsKey(key)) {
                return false;
            }
            rel_file_records.put(key, line);
            save_rel_file();
            return true;
        }
    }

    private boolean delete_rel_file() {
        String line = format_rel_file_record();
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            String key = "";
            key = String.valueOf(ws_rrn).trim();
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "DELETE FROM rel_file_vsam WHERE key_col = ?", key
            );
            if (rows == 0) {
                return false;
            }
            save_rel_file();
            return true;
        } else {
            String key = String.valueOf(ws_rrn).trim();
            if (!rel_file_records.containsKey(key)) {
                return false;
            }
            rel_file_records.remove(key);
            save_rel_file();
            return true;
        }
    }

    private boolean delete_rel_file_key(String key) {
        if (key == null) return false;
        boolean hasDb = false;
        try {
            if (com.systema.modernized.SpringContextHelper.jdbcTemplate != null) {
                hasDb = true;
            }
        } catch (Throwable t) {}
        if (hasDb) {
            int rows = com.systema.modernized.SpringContextHelper.jdbcTemplate.update(
                "DELETE FROM rel_file_vsam WHERE key_col = ?", key.trim()
            );
            if (rows == 0) {
                return false;
            }
            save_rel_file();
            return true;
        } else {
            if (!rel_file_records.containsKey(key.trim())) {
                return false;
            }
            rel_file_records.remove(key.trim());
            save_rel_file();
            return true;
        }
    }

    private boolean start_rel_file(String key, String op) {
        return start_rel_file(key, op, "WS-RRN");
    }

    private boolean start_rel_file(String key, String op, String keyName) {
        if (key == null) return false;
        rel_file_eof = false;
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
                rel_file_db_list = com.systema.modernized.SpringContextHelper.jdbcTemplate.query(
                    "SELECT record_col FROM rel_file_vsam WHERE key_col " + op_sql + " ? ORDER BY key_col",
                    (rs, rowNum) -> rs.getString("record_col"), key.trim()
                );
            }
            if (rel_file_db_list.isEmpty()) {
                return false;
            }
            rel_file_iterator = rel_file_db_list.iterator();
            return true;
        } else {
            String queryKey = keyName.toUpperCase();
            java.util.List<String> sortedRecords = new java.util.ArrayList<>(rel_file_records.values());
            boolean matched = false;
            if (!matched) {
                sortedRecords.sort((r1, r2) -> {
                    return r1.compareTo(r2);
                });
            }
            int skipCount = 0;
            boolean found = false;
            String targetKey = key.trim();
            for (String record : sortedRecords) {
                String val = "";
                boolean isAlt = false;
                if (!isAlt) {
                    val = targetKey;
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
                return false;
            }
            rel_file_iterator = sortedRecords.iterator();
            for (int i = 0; i < skipCount; i++) {
                if (rel_file_iterator.hasNext()) rel_file_iterator.next();
            }
            return true;
        }
    }

    private void close_rel_file() {
        save_rel_file();
        rel_file_records.clear();
        rel_file_db_list.clear();
        rel_file_iterator = null;
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
        if (!skipToNextSentence) { open_rel_file("OUTPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rrn = 1; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { r_data = padString(String.valueOf("RECORD ONE"), 20); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { write_rel_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rrn = 2; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { r_data = padString(String.valueOf("RECORD TWO"), 20); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { write_rel_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rrn = 3; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { r_data = padString(String.valueOf("RECORD THREE"), 20); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { write_rel_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_rel_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { open_rel_file("INPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rrn = 2; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { read_rel_file_key(String.valueOf(ws_rrn), "WS-RRN"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            {
                    writeBytes(r_data.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_rrn = 1; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { read_rel_file_key(String.valueOf(ws_rrn), "WS-RRN"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            {
                    writeBytes(r_data.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_rel_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { if (true) { programExited = true; return; } }
    }

    public static void main(String[] args) {
        try {
            new Relfile().execute();
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