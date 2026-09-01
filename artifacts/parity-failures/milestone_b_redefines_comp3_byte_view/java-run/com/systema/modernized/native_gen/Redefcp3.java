package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Redefcp3 {

    public int return_code = 0;
    // --- REDEFINES Backing Storage ---
    private final byte[] ws_group_backing = new byte[4];
    {
        java.util.Arrays.fill(ws_group_backing, (byte) 32);
    }

    // --- REDEFINES Accessors ---
    public String get_ws_group() {
        int off = 0;
        return new String(ws_group_backing, off, 4, java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    public void set_ws_group(String val) {
        int off = 0;
        if (val == null) val = "";
        String padded = padString(val, 4);
        byte[] src = padded.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        System.arraycopy(src, 0, ws_group_backing, off, 4);
    }

    public BigDecimal get_c() {
        int off = 0;
        return new com.systema.modernized.runtime.CobolNumeric(ws_group_backing, off, 4, new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).getValue();
    }

    public void set_c(BigDecimal val) {
        int off = 0;
        new com.systema.modernized.runtime.CobolNumeric(ws_group_backing, off, 4, new com.systema.modernized.runtime.CobolNumericSpec(true, 6, 2, com.systema.modernized.runtime.CobolUsage.COMP_3, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false)).assign(val);
    }

    public String get_d() {
        int off = 0;
        return new String(ws_group_backing, off, 3, java.nio.charset.StandardCharsets.ISO_8859_1);
    }

    public void set_d(String val) {
        int off = 0;
        if (val == null) val = "";
        String padded = padString(val, 3);
        byte[] src = padded.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        System.arraycopy(src, 0, ws_group_backing, off, 3);
    }

    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    public byte[] get_ws_group_bytes() {
        return ws_group_backing;
    }
    private void populate_ws_group(String line) {
        if (line == null) line = "";
        byte[] src = line.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        System.arraycopy(src, 0, ws_group_backing, 0, Math.min(src.length, 4));
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
        if (!skipToNextSentence) { set_c(BigDecimal.ZERO); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { set_c(new BigDecimal("-12.34")); }
        skipToNextSentence = false;
        {
        writeBytes(get_ws_group_bytes());
        System.out.write(10);
        System.out.flush();
    }
        skipToNextSentence = false;
        if (true) { programExited = true; return; }
    }

    public static void main(String[] args) {
        try {
            new Redefcp3().execute();
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