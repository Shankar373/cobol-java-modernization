package com.systema.modernized;

public class Db2ErrorMapper {
    public static int getSqlCode(Exception e) {
        if (e.getClass().getName().equals("org.springframework.dao.EmptyResultDataAccessException")) {
            return 100;
        }
        Throwable cause = e.getCause() != null ? e.getCause() : e;
        if (cause instanceof java.sql.SQLException) {
            java.sql.SQLException sqle = (java.sql.SQLException) cause;
            String state = sqle.getSQLState();
            if (state != null) {
                if ("23000".equals(state) || "23505".equals(state)) return -803; // unique constraint violation
                if ("42P01".equals(state) || "42S02".equals(state)) return -204; // table not found
                if ("42703".equals(state) || "42S22".equals(state)) return -206; // column not found
                if ("40001".equals(state))                           return -911; // deadlock or timeout
                if ("08000".equals(state) || "08006".equals(state)) return -900; // connection error
            }
            int code = sqle.getErrorCode();
            return code != 0 ? -Math.abs(code) : -1;
        }
        return -1;
    }

    public static String getSqlState(Exception e) {
        if (e.getClass().getName().equals("org.springframework.dao.EmptyResultDataAccessException")) {
            return "02000";
        }
        Throwable cause = e.getCause() != null ? e.getCause() : e;
        if (cause instanceof java.sql.SQLException) {
            java.sql.SQLException sqle = (java.sql.SQLException) cause;
            String state = sqle.getSQLState();
            if (state == null) return "99999";
            if ("42P01".equals(state) || "42S02".equals(state)) return "42704"; // table undefined
            if ("42703".equals(state) || "42S22".equals(state)) return "42704"; // column undefined
            if ("23000".equals(state) || "23505".equals(state)) return "23000"; // constraint violation
            if ("40001".equals(state))                           return "40001"; // deadlock
            if ("08000".equals(state) || "08006".equals(state)) return "08001"; // connection error
            return state;
        }
        return "99999";
    }
}