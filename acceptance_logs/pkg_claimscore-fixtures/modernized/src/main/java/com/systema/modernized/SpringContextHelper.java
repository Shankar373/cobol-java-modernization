package com.systema.modernized;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.PlatformTransactionManager;

public class SpringContextHelper {
    public static JdbcTemplate jdbcTemplate;
    public static PlatformTransactionManager transactionManager;
}