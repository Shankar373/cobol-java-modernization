package com.systema.modernized.native_gen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Objects;

public class Filestat01 {

    public int return_code = 0;
    public String file_rec = "                              ";
    public String ws_file_status = "  ";
    public String ws_eof_flag = "N";
    public int ws_count = 0;
    public String ws_r1 = "RECORD_01                     ";
    public String ws_r2 = "RECORD_02                     ";
    public String ws_r3 = "RECORD_03                     ";
    {  // Initialise redefines values
    }

    private int checkBounds(int subscript, int minOccurs, String dependingVarName, int dependingVarValue) {
        if (subscript < minOccurs || subscript > dependingVarValue) {
            throw new IndexOutOfBoundsException("Subscript " + subscript + " out of active bounds [" + minOccurs + ", " + dependingVarValue + "] depending on " + dependingVarName);
        }
        return subscript - 1;
    }


    private String resolve_path_seq_file() {
        String resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("SEQ-FILE");
        if (resolvedPath == null) {
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment("/run/outfile.txt");
        }
        if (resolvedPath == null) {
            String cleanLogical = "SEQ-FILE";
            if (cleanLogical.startsWith("UT-S-")) {
                cleanLogical = cleanLogical.substring(5);
            } else if (cleanLogical.startsWith("UT_S_")) {
                cleanLogical = cleanLogical.substring(5);
            }
            resolvedPath = com.systema.modernized.JclExecutionContext.getDdAssignment(cleanLogical);
        }
        if (resolvedPath == null) {
            resolvedPath = "/run/outfile.txt";
        }
        return resolvedPath;
    }

    private java.io.InputStream seq_file_stream_in;
    private java.io.OutputStream seq_file_stream_out;

    private void open_seq_file() {
        open_seq_file("INPUT");
    }

    private void open_seq_file(String mode) {
        try {
            close_seq_file();
            if ("INPUT".equalsIgnoreCase(mode)) {
                seq_file_stream_in = new java.io.BufferedInputStream(new java.io.FileInputStream(resolve_path_seq_file()));
            } else if ("OUTPUT".equalsIgnoreCase(mode)) {
                java.nio.file.Path parent = Paths.get(resolve_path_seq_file()).getParent();
                if (parent != null) Files.createDirectories(parent);
                seq_file_stream_out = new java.io.BufferedOutputStream(new java.io.FileOutputStream(resolve_path_seq_file()));
            }
            ws_file_status = "00";
        } catch (IOException e) {
            ws_file_status = "35";
        }
    }

    private boolean read_seq_file() {
        try {
            if (seq_file_stream_in == null) return false;
            byte[] buf = new byte[30];
            int bytesRead = 0;
            while (bytesRead < 30) {
                int r = seq_file_stream_in.read(buf, bytesRead, 30 - bytesRead);
                if (r == -1) break;
                bytesRead += r;
            }
            if (bytesRead < 30) {
                ws_file_status = "10";
                return false;
            }
            file_rec = new String(buf, 0, 30, java.nio.charset.StandardCharsets.ISO_8859_1);
            ws_file_status = "00";
            return true;
        } catch (IOException e) {
            ws_file_status = "30";
            return false;
        }
    }

    private void write_seq_file() {
        try {
            if (seq_file_stream_out == null) return;
            byte[] buf = new byte[30];
            byte[] c_file_rec = padString(file_rec, 30).getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
            System.arraycopy(c_file_rec, 0, buf, 0, Math.min(c_file_rec.length, 30));
            seq_file_stream_out.write(buf);
            seq_file_stream_out.flush();
            ws_file_status = "00";
        } catch (IOException e) {
            ws_file_status = "30";
        }
    }

    private void close_seq_file() {
        try {
            if (seq_file_stream_in != null) { seq_file_stream_in.close(); seq_file_stream_in = null; }
            if (seq_file_stream_out != null) { seq_file_stream_out.close(); seq_file_stream_out = null; }
            ws_file_status = "00";
        } catch (IOException e) {
            ws_file_status = "30";
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
        if (!skipToNextSentence) { open_seq_file("OUTPUT"); }
        for (ws_count = 1; !(ws_count > 3) && !programExited; ws_count += 1) {
        if (skipToNextSentence) break;
        if (ws_count == 1) {
        if (!skipToNextSentence) { file_rec = padString(String.valueOf(ws_r1), 30); }
        }
        if (ws_count == 2) {
        if (!skipToNextSentence) { file_rec = padString(String.valueOf(ws_r2), 30); }
        }
        if (ws_count == 3) {
        if (!skipToNextSentence) { file_rec = padString(String.valueOf(ws_r3), 30); }
        }
        if (!skipToNextSentence) { write_seq_file(); }
        if (!skipToNextSentence) {
            {
                    writeBytes("Write: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        }
        if (!skipToNextSentence) { close_seq_file(); }
        if (!skipToNextSentence) {
            {
                    writeBytes("Close: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) { open_seq_file("INPUT"); }
        if (!skipToNextSentence) {
            {
                    writeBytes("Reopen: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                    System.out.write(10);
                    System.out.flush();
                }
        }
        if (!skipToNextSentence) { ws_eof_flag = padString(String.valueOf("N"), 1); }
        while (!(ws_eof_flag.equals("Y")) && !programExited) {
        if (skipToNextSentence) break;
        if (!skipToNextSentence) {
            if (!read_seq_file()) {
                        if (!skipToNextSentence) {
                        {
                                writeBytes("EOF: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                System.out.write(10);
                                System.out.flush();
                            }
                    }
                        if (!skipToNextSentence) { ws_eof_flag = padString(String.valueOf("Y"), 1); }
                    } else {
                        if (!skipToNextSentence) {
                        {
                                writeBytes("Rec: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                writeBytes(file_rec.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                System.out.write(10);
                                System.out.flush();
                            }
                    }
                        if (!skipToNextSentence) {
                        {
                                writeBytes("FS: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                System.out.write(10);
                                System.out.flush();
                            }
                    }
                    }
        }
        }
        if (!skipToNextSentence) {
            if (!read_seq_file()) {
                        if (!skipToNextSentence) {
                        {
                                writeBytes("Past EOF: ".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                writeBytes(ws_file_status.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                System.out.write(10);
                                System.out.flush();
                            }
                    }
                    } else {
                        if (!skipToNextSentence) {
                        {
                                writeBytes("Error: should not read".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));
                                System.out.write(10);
                                System.out.flush();
                            }
                    }
                    }
        }
        if (!skipToNextSentence) { close_seq_file(); }
        if (!skipToNextSentence) { if (true) { throw new StopRunException(); } }
    }

    public static void main(String[] args) {
        try {
            new Filestat01().execute();
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