package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Truncar {

    public int return_code = 0;
    public String ws_group = "";
    public com.systema.modernized.runtime.CobolNumeric a = new com.systema.modernized.runtime.CobolNumeric(new com.systema.modernized.runtime.CobolNumericSpec(false, 7, 3, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false));
    public String filler_1 = "|";
    public com.systema.modernized.runtime.CobolNumeric b = new com.systema.modernized.runtime.CobolNumeric(new com.systema.modernized.runtime.CobolNumericSpec(false, 6, 2, com.systema.modernized.runtime.CobolUsage.DISPLAY, com.systema.modernized.runtime.CobolSignPosition.TRAILING, false));
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    public byte[] get_ws_group_bytes() {
        byte[] c_0 = a.toStorageImage();
        byte[] c_1 = filler_1.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        byte[] c_2 = b.toStorageImage();
        byte[] res = new byte[c_0.length + c_1.length + c_2.length];
        System.arraycopy(c_0, 0, res, 0, c_0.length);
        System.arraycopy(c_1, 0, res, 0 + c_0.length, c_1.length);
        System.arraycopy(c_2, 0, res, 0 + c_0.length + c_1.length, c_2.length);
        return res;
    }
    private void populate_ws_group(String line) {
        if (line == null) line = "";
        ws_group = line;
        if (line.length() >= 7) {
            String val = line.substring(0, 7).trim();
            a.assign(val.isEmpty() ? BigDecimal.ZERO : new BigDecimal(val).movePointLeft(3));
        }
        if (line.length() >= 8) {
            String val = line.substring(7, 8).trim();
            filler_1 = val;
        }
        if (line.length() >= 14) {
            String val = line.substring(8, 14).trim();
            b.assign(val.isEmpty() ? BigDecimal.ZERO : new BigDecimal(val).movePointLeft(2));
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
        if (!skipToNextSentence) {
            a.assign(BigDecimal.ZERO, com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);
                    b.assign(BigDecimal.ZERO, com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);
        }
        skipToNextSentence = false;
        if (!skipToNextSentence) { a.assign(new BigDecimal("1.236"), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { b.assign(new BigDecimal("0"), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED); }
        skipToNextSentence = false;
        if (!skipToNextSentence) { b.assign(a.getValue(), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED); }
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
            new Truncar().execute();
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