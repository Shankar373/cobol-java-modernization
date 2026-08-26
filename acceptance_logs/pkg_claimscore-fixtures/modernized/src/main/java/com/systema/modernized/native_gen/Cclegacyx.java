package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Cclegacyx {

    public int return_code = 0;
    public int ws_index = 1;
    // --- REDEFINES Backing Storage ---
    private final char[] ws_area_backing = new char[21];
    {
        java.util.Arrays.fill(ws_area_backing, ' ');
    }

    // --- REDEFINES Accessors ---
    public String get_ws_area() {
        int off = 0;
        return new String(ws_area_backing, off, 21);
    }

    public void set_ws_area(String val) {
        int off = 0;
        if (val == null) val = "";
        String padded = String.format("%-" + 21 + "s", val);
        if (padded.length() > 21) padded = padded.substring(0, 21);
        for (int i = 0; i < 21; i++) {
            ws_area_backing[off + i] = padded.charAt(i);
        }
    }

    public String get_ws_code() {
        int off = 0;
        return new String(ws_area_backing, off, 2);
    }

    public void set_ws_code(String val) {
        int off = 0;
        if (val == null) val = "";
        String padded = String.format("%-" + 2 + "s", val);
        if (padded.length() > 2) padded = padded.substring(0, 2);
        for (int i = 0; i < 2; i++) {
            ws_area_backing[off + i] = padded.charAt(i);
        }
    }

    public BigDecimal get_ws_amount() {
        int off = 2;
        String s = new String(ws_area_backing, off, 9).trim();
        return parseSigned(s, 2);
    }

    public void set_ws_amount(BigDecimal val) {
        int off = 2;
        if (val == null) val = BigDecimal.ZERO;
        long unscaled = val.movePointRight(2).longValue();
        String formatted = formatSigned(unscaled, 9, true);
        for (int i = 0; i < 9; i++) {
            ws_area_backing[off + i] = formatted.charAt(i);
        }
    }

    public String get_ws_flags() {
        int off = 11;
        return new String(ws_area_backing, off, 10);
    }

    public void set_ws_flags(String val) {
        int off = 11;
        if (val == null) val = "";
        String padded = String.format("%-" + 10 + "s", val);
        if (padded.length() > 10) padded = padded.substring(0, 10);
        for (int i = 0; i < 10; i++) {
            ws_area_backing[off + i] = padded.charAt(i);
        }
    }

    public String get_ws_flag_table() {
        int off = 11;
        return new String(ws_area_backing, off, 10);
    }

    public void set_ws_flag_table(String val) {
        int off = 11;
        if (val == null) val = "";
        String padded = String.format("%-" + 10 + "s", val);
        if (padded.length() > 10) padded = padded.substring(0, 10);
        for (int i = 0; i < 10; i++) {
            ws_area_backing[off + i] = padded.charAt(i);
        }
    }

    public String get_ws_flag(int idx) {
        int off = 11 + (idx - 1) * 1;
        return new String(ws_area_backing, off, 10);
    }

    public void set_ws_flag(int idx, String val) {
        int off = 11 + (idx - 1) * 1;
        if (val == null) val = "";
        String padded = String.format("%-" + 10 + "s", val);
        if (padded.length() > 10) padded = padded.substring(0, 10);
        for (int i = 0; i < 10; i++) {
            ws_area_backing[off + i] = padded.charAt(i);
        }
    }

    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }

    private void populate_ws_area(String line) {
        if (line == null) line = "";
        set_ws_area(line);
        if (line.length() >= 2) {
            String val = line.substring(0, 2).trim();
            set_ws_code(val);
        }
        if (line.length() >= 11) {
            String val = line.substring(2, 11).trim();
            set_ws_amount(parseSigned(val, 2));
        }
        if (line.length() >= 21) {
            String val = line.substring(11, 21).trim();
            set_ws_flags(val);
        }
        if (line.length() >= 22) {
            set_ws_flag(1, line.substring(21, 22).trim());
        }
        if (line.length() >= 23) {
            set_ws_flag(2, line.substring(22, 23).trim());
        }
        if (line.length() >= 24) {
            set_ws_flag(3, line.substring(23, 24).trim());
        }
        if (line.length() >= 25) {
            set_ws_flag(4, line.substring(24, 25).trim());
        }
        if (line.length() >= 26) {
            set_ws_flag(5, line.substring(25, 26).trim());
        }
        if (line.length() >= 27) {
            set_ws_flag(6, line.substring(26, 27).trim());
        }
        if (line.length() >= 28) {
            set_ws_flag(7, line.substring(27, 28).trim());
        }
        if (line.length() >= 29) {
            set_ws_flag(8, line.substring(28, 29).trim());
        }
        if (line.length() >= 30) {
            set_ws_flag(9, line.substring(29, 30).trim());
        }
        if (line.length() >= 31) {
            set_ws_flag(10, line.substring(30, 31).trim());
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
        // UNSUPPORTED: UNKNOWN
        skipToNextSentence = false;
        // UNSUPPORTED: UNKNOWN
        skipToNextSentence = false;
        if (Objects.equals(get_ws_code(), "MV")) {
        if (!skipToNextSentence) { set_ws_code(padString(String.valueOf("MOTOR"), 2)); }
        } else if (Objects.equals(get_ws_code(), "HE")) {
        if (!skipToNextSentence) { set_ws_code(padString(String.valueOf("HEALTH"), 2)); }
        } else {
        if (!skipToNextSentence) { set_ws_code(padString(String.valueOf("XX"), 2)); }
        }
        for (ws_index = 1; !(ws_index > 10); ws_index += 1) {
        if (skipToNextSentence) break;
        if (!skipToNextSentence) { set_ws_flag(ws_index, padString(String.valueOf("Y"), 1)); }
        }
        skipToNextSentence = false;
        // UNSUPPORTED: UNKNOWN
        skipToNextSentence = false;
        skipToNextSentence = false;
        // UNSUPPORTED: UNKNOWN
        skipToNextSentence = false;
        if (true) { programExited = true; return; }
    }

    public static void main(String[] args) {
        try {
            new Cclegacyx().execute();
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