package com.systema.modernized;
public class SpringContextHelper {
    public static class MockResultSet {
        public String getString(String c) { return null; }
        public String getString(int idx) { return null; }
    }
    public interface MockRowMapper<T> { T mapRow(MockResultSet rs, int r) throws Exception; }
    public static class MockJdbcTemplate {
        public void execute(String sql) {}
        public int update(String sql, Object... args) { return 0; }
    }
    public static MockJdbcTemplate jdbcTemplate = null;
}