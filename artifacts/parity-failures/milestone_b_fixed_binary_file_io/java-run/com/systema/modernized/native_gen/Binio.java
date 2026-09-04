package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Binio {

    public int return_code = 0;
    public String bin_rec = "";
    public com.systema.modernized.runtime.CobolNumeric field_comp3 = new com.systema.modernized.runtime.CobolNumeric(new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false));
    public int field_zoned = 0;
    public String ws_var = "";
    public com.systema.modernized.runtime.CobolNumeric ws_comp3 = new com.systema.modernized.runtime.CobolNumeric(new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false));
    public int ws_zoned = 0;
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    public byte[] get_bin_rec_bytes() {
        byte[] c_0 = field_comp3.toStorageImage();
        byte[] c_1 = formatSigned(field_zoned, 4, true).getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] res = new byte[c_0.length + c_1.length];
        System.arraycopy(c_0, 0, res, 0, c_0.length);
        System.arraycopy(c_1, 0, res, 0 + c_0.length, c_1.length);
        return res;
    }
    public byte[] get_ws_var_bytes() {
        byte[] c_0 = ws_comp3.toStorageImage();
        byte[] c_1 = formatSigned(ws_zoned, 4, true).getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] res = new byte[c_0.length + c_1.length];
        System.arraycopy(c_0, 0, res, 0, c_0.length);
        System.arraycopy(c_1, 0, res, 0 + c_0.length, c_1.length);
        return res;
    }
    private void populate_bin_rec(String line) {
        if (line == null) line = "";
        bin_rec = line;
        if (line.length() >= 6) {
            String val = line.substring(0, 6).trim();
            field_comp3.assign(parseSigned(val, 2));
        }
        if (line.length() >= 10) {
            String val = line.substring(6, 10).trim();
            field_zoned = (int) parseSignedLong(val);
        }
    }

    private void populate_ws_var(String line) {
        if (line == null) line = "";
        ws_var = line;
        if (line.length() >= 6) {
            String val = line.substring(0, 6).trim();
            ws_comp3.assign(parseSigned(val, 2));
        }
        if (line.length() >= 10) {
            String val = line.substring(6, 10).trim();
            ws_zoned = (int) parseSignedLong(val);
        }
    }


    private String resolve_path_bin_file() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("BIN-FILE");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("/run/BINFILE.DAT");
        }
        if (resolvedPath == null) {
            String cleanLogical = "BIN-FILE";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "/run/BINFILE.DAT";
        }
        return resolvedPath;
    }

    private java.io.InputStream bin_file_stream_in;
    private java.io.OutputStream bin_file_stream_out;

    private void open_bin_file() {
        open_bin_file("INPUT");
    }

    private void open_bin_file(String mode) {
        try {
            close_bin_file();
            if ("INPUT".equalsIgnoreCase(mode)) {
                bin_file_stream_in = new java.io.BufferedInputStream(new java.io.FileInputStream(resolve_path_bin_file()));
            } else if ("OUTPUT".equalsIgnoreCase(mode)) {
                java.nio.file.Path parent = Paths.get(resolve_path_bin_file()).getParent();
                if (parent != null) Files.createDirectories(parent);
                bin_file_stream_out = new java.io.BufferedOutputStream(new java.io.FileOutputStream(resolve_path_bin_file()));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private boolean read_bin_file() {
        try {
            if (bin_file_stream_in == null) return false;
            byte[] buf = new byte[9];
            int bytesRead = 0;
            while (bytesRead < 9) {
                int r = bin_file_stream_in.read(buf, bytesRead, 9 - bytesRead);
                if (r == -1) break;
                bytesRead += r;
            }
            if (bytesRead < 9) {
                return false;
            }
            field_comp3.assign(new com.systema.modernized.runtime.CobolNumeric(buf, 0, 4, new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).getValue());
            field_zoned = (int) new com.systema.modernized.runtime.CobolNumeric(buf, 4, 5, new com.systema.modernized.runtime.CobolNumericSpec(true, 4, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, true)).getValue().intValue();
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    private void write_bin_file() {
        try {
            if (bin_file_stream_out == null) return;
            byte[] buf = new byte[9];
            byte[] c_field_comp3 = field_comp3.toStorageImage();
            System.arraycopy(c_field_comp3, 0, buf, 0, Math.min(c_field_comp3.length, 4));
            byte[] c_field_zoned = new com.systema.modernized.runtime.CobolNumeric(java.math.BigDecimal.valueOf(field_zoned), new com.systema.modernized.runtime.CobolNumericSpec(true, 4, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, true)).toStorageImage();
            System.arraycopy(c_field_zoned, 0, buf, 4, Math.min(c_field_zoned.length, 5));
            bin_file_stream_out.write(buf);
            bin_file_stream_out.flush();
        } catch (IOException e) {
        }
    }

    private void close_bin_file() {
        try {
            if (bin_file_stream_in != null) { bin_file_stream_in.close(); bin_file_stream_in = null; }
            if (bin_file_stream_out != null) { bin_file_stream_out.close(); bin_file_stream_out = null; }
        } catch (IOException e) {
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
        if (!skipToNextSentence) { open_bin_file("OUTPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_comp3.assign(new BigDecimal("-12.34"), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { ws_zoned = -5678; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { field_comp3.assign(ws_comp3.getValue(), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { field_zoned = ws_zoned; }
        skipToNextSentence = false;
        if (!skipToNextSentence) { write_bin_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_bin_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) {
            field_comp3.assign(BigDecimal.ZERO, com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);
                    field_zoned = 0;
        }
        skipToNextSentence = false;
        if (!skipToNextSentence) { open_bin_file("INPUT"); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { read_bin_file(); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { close_bin_file(); }
        skipToNextSentence = false;
        {
        writeBytes(new com.systema.modernized.runtime.CobolNumeric(field_comp3.getValue(), new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).toDisplayString().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
        System.out.write(10);
        System.out.flush();
    }
        skipToNextSentence = false;
        {
        writeBytes(new com.systema.modernized.runtime.CobolNumeric(java.math.BigDecimal.valueOf(field_zoned), new com.systema.modernized.runtime.CobolNumericSpec(true, 4, 0, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, true)).toDisplayString().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
        System.out.write(10);
        System.out.flush();
    }
        skipToNextSentence = false;
        if (true) { programExited = true; return; }
    }

    public static void main(String[] args) {
        try {
            new Binio().execute();
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