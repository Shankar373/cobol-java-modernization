package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Ccrept01 {

    public int return_code = 0;
    public String audit_line = "                                                                                                                                                                                                                            ";
    public String exception_line = "                                                                                                                                                                                                                            ";
    public String report_line = "                                                                                                                                                                ";
    public String ws_audit_eof = "N";
    public String ws_exc_eof = "N";
    public int ws_audit_count = 0;
    public int ws_exception_count = 0;
    public int ws_review_count = 0;
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }


    private String resolve_path_audit_in() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("AUDIT-IN");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/out/claim-audit.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "AUDIT-IN";
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

    private BufferedReader audit_in_reader;
    private void open_audit_in() {
        try {
            audit_in_reader = Files.newBufferedReader(Paths.get(resolve_path_audit_in()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private boolean read_audit_in() {
        try {
            String line = audit_in_reader.readLine();
            if (line == null) {
                return false;
            } else {
                String val_audit_line = (line.length() >= 220) ? line.substring(0, 220).trim() : (line.length() > 0 ? line.substring(0).trim() : "");
                audit_line = val_audit_line;
            }
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    private void close_audit_in() {
        try {
            if (audit_in_reader != null) audit_in_reader.close();
        } catch (IOException e) {
        }
    }

    private String resolve_path_exception_in() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("EXCEPTION-IN");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/out/claim-exceptions.dat");
        }
        if (resolvedPath == null) {
            String cleanLogical = "EXCEPTION-IN";
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

    private BufferedReader exception_in_reader;
    private void open_exception_in() {
        try {
            exception_in_reader = Files.newBufferedReader(Paths.get(resolve_path_exception_in()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private boolean read_exception_in() {
        try {
            String line = exception_in_reader.readLine();
            if (line == null) {
                return false;
            } else {
                String val_exception_line = (line.length() >= 220) ? line.substring(0, 220).trim() : (line.length() > 0 ? line.substring(0).trim() : "");
                exception_line = val_exception_line;
            }
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    private void close_exception_in() {
        try {
            if (exception_in_reader != null) exception_in_reader.close();
        } catch (IOException e) {
        }
    }

    private String resolve_path_report_out() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("REPORT-OUT");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("data/out/eod-claims-report.txt");
        }
        if (resolvedPath == null) {
            String cleanLogical = "REPORT-OUT";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "data/out/eod-claims-report.txt";
        }
        return resolvedPath;
    }

    private BufferedWriter report_out_writer;
    private void open_report_out() {
        try {
            java.nio.file.Path parent = Paths.get(resolve_path_report_out()).getParent();
            if (parent != null) Files.createDirectories(parent);
            report_out_writer = Files.newBufferedWriter(Paths.get(resolve_path_report_out()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private void write_report_out() {
        try {
            report_out_writer.write(String.format("%-160s", report_line));
            report_out_writer.newLine();
        } catch (IOException e) {
        }
    }

    private void close_report_out() {
        try {
            if (report_out_writer != null) report_out_writer.close();
        } catch (IOException e) {
        }
    }

    private boolean programExited = false;
    private int nextParagraphIndex = -1;
    private boolean skipToNextSentence = false;
    private final int total_paras = 4;

    public static class StopRunException extends RuntimeException {}

    private int getParagraphIndex(String name) {
        if (name == null) return -1;
        switch (name) {
            case "main_section": return 0;
            case "read_audit": return 1;
            case "read_exceptions": return 2;
            case "write_report": return 3;
            default: return -1;
        }
    }

    private void runParagraph(int idx) {
        if (programExited) return;
        switch (idx) {
            case 0: main_section(); break;
            case 1: read_audit(); break;
            case 2: read_exceptions(); break;
            case 3: write_report(); break;
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
        while (i < 4) {
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
            open_audit_in();
                    open_exception_in();
        }
        if (!skipToNextSentence) { open_report_out(); }
        if (!skipToNextSentence) {
            perform("read_audit", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        if (!skipToNextSentence) {
            perform("read_exceptions", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        if (!skipToNextSentence) {
            perform("write_report", null);
                    if (nextParagraphIndex != -1 || programExited) return;
        }
        if (!skipToNextSentence) {
            close_audit_in();
                    close_exception_in();
                    close_report_out();
        }
        if (!skipToNextSentence) { return_code = 0; }
        if (true) { programExited = true; return; }
    }

    private void read_audit() {
        skipToNextSentence = false;
        while (!(ws_audit_eof.equals("Y"))) {
        if (skipToNextSentence) break;
        if (!read_audit_in()) {
            if (!skipToNextSentence) { ws_audit_eof = padString(String.valueOf("Y"), 1); }
        } else {
            if (!skipToNextSentence) { ws_audit_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_audit_count + 1)), 7, 0, false).intValue(); }
            if (audit_line.substring(24, 37).equals("MANUAL_REVIEW")) {
            if (!skipToNextSentence) { ws_review_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_review_count + 1)), 7, 0, false).intValue(); }
            }
        }
        }
    }

    private void read_exceptions() {
        skipToNextSentence = false;
        while (!(ws_exc_eof.equals("Y"))) {
        if (skipToNextSentence) break;
        if (!read_exception_in()) {
            if (!skipToNextSentence) { ws_exc_eof = padString(String.valueOf("Y"), 1); }
        } else {
            if (!skipToNextSentence) { ws_exception_count = com.systema.modernized.CobolFormatHelper.truncateToPic(BigDecimal.valueOf((long)(ws_exception_count + 1)), 7, 0, false).intValue(); }
        }
        }
    }

    private void write_report() {
        skipToNextSentence = false;
        if (!skipToNextSentence) { report_line = padString(String.valueOf("CLAIMSCORE - END OF DAY CLAIMS REPORT"), 160); }
        if (!skipToNextSentence) { write_report_out(); }
        if (!skipToNextSentence) { report_line = padString(String.valueOf("AUDIT RECORDS         : " + String.valueOf(ws_audit_count)), 160); }
        if (!skipToNextSentence) { write_report_out(); }
        if (!skipToNextSentence) { report_line = padString(String.valueOf("EXCEPTIONS            : " + String.valueOf(ws_exception_count)), 160); }
        if (!skipToNextSentence) { write_report_out(); }
        if (!skipToNextSentence) { report_line = padString(String.valueOf("MANUAL REVIEWS        : " + String.valueOf(ws_review_count)), 160); }
        if (!skipToNextSentence) { write_report_out(); }
        if (!skipToNextSentence) { report_line = padString(String.valueOf("STATUS: CLAIMS BATCH COMPLETED"), 160); }
        if (!skipToNextSentence) { write_report_out(); }
    }

    public static void main(String[] args) {
        try {
            new Ccrept01().execute();
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