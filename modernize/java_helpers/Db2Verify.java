package com.systema.modernized;

import java.sql.*;
import java.util.*;
import java.io.*;

public class Db2Verify {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Error: Missing SQL query argument.");
            System.exit(1);
        }
        String sql = args[0];
        String dbUrl = System.getenv("DB2_URL");
        String dbUser = System.getenv("DB2_USERNAME");
        String dbPass = System.getenv("DB2_PASSWORD");
        String dbSchema = System.getenv("DB2_SCHEMA");

        if (dbUrl == null || dbUser == null || dbPass == null) {
            System.err.println("Error: Missing environment variables DB2_URL, DB2_USERNAME, or DB2_PASSWORD.");
            System.exit(1);
        }

        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;
        try {
            Class.forName("com.ibm.db2.jcc.DB2Driver");
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
            
            if (dbSchema != null && !dbSchema.trim().isEmpty()) {
                Statement sSchema = conn.createStatement();
                sSchema.execute("SET SCHEMA " + dbSchema.trim());
                sSchema.close();
            }

            stmt = conn.createStatement();
            boolean isResultSet = stmt.execute(sql);
            if (isResultSet) {
                rs = stmt.getResultSet();
                ResultSetMetaData md = rs.getMetaData();
                int columns = md.getColumnCount();
                List<Map<String, Object>> list = new ArrayList<>();
                while (rs.next()) {
                    Map<String, Object> row = new LinkedHashMap<>();
                    for (int i = 1; i <= columns; i++) {
                        row.put(md.getColumnName(i).toUpperCase(), rs.getObject(i));
                    }
                    list.add(row);
                }
                // Print as custom format that Python can parse easily
                System.out.println("---JSON_START---");
                System.out.println(toJSON(list));
                System.out.println("---JSON_END---");
            } else {
                int updateCount = stmt.getUpdateCount();
                System.out.println("---JSON_START---");
                System.out.println("{\"update_count\": " + updateCount + "}");
                System.out.println("---JSON_END---");
            }
        } catch (Exception e) {
            System.err.println("DB2 Execution Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(2);
        } finally {
            try { if (rs != null) rs.close(); } catch (Exception e) {}
            try { if (stmt != null) stmt.close(); } catch (Exception e) {}
            try { if (conn != null) conn.close(); } catch (Exception e) {}
        }
    }

    private static String toJSON(List<Map<String, Object>> list) {
        StringBuilder sb = new StringBuilder();
        sb.append("[\n");
        for (int i = 0; i < list.size(); i++) {
            Map<String, Object> row = list.get(i);
            sb.append("  {");
            Iterator<Map.Entry<String, Object>> it = row.entrySet().iterator();
            while (it.hasNext()) {
                Map.Entry<String, Object> entry = it.next();
                sb.append("\"").append(entry.getKey()).append("\": ");
                Object val = entry.getValue();
                if (val == null) {
                    sb.append("null");
                } else if (val instanceof Number || val instanceof Boolean) {
                    sb.append(val);
                } else {
                    sb.append("\"").append(val.toString().replace("\"", "\\\"")).append("\"");
                }
                if (it.hasNext()) {
                    sb.append(", ");
                }
            }
            sb.append("}");
            if (i < list.size() - 1) {
                sb.append(",\n");
            }
        }
        sb.append("\n]");
        return sb.toString();
    }
}
