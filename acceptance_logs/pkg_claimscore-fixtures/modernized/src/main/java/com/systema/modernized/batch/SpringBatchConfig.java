package com.systema.modernized.batch;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
public class SpringBatchConfig {

    @Bean
    public Job modernizedJob(JobRepository jobRepository, Step step1) {
        return new JobBuilder("modernizedJob", jobRepository)
                .start(step1)
                .build();
    }

    @Bean
    public Step step1(JobRepository jobRepository, PlatformTransactionManager transactionManager, org.springframework.jdbc.core.JdbcTemplate jdbcTemplate) {
        String entryClass = "Ccmain01";
        return new StepBuilder("step1", jobRepository)
                .tasklet((contribution, chunkContext) -> {
                    com.systema.modernized.SpringContextHelper.jdbcTemplate = jdbcTemplate;
                    com.systema.modernized.SpringContextHelper.transactionManager = transactionManager;
                    try {
                        new com.systema.modernized.native_gen.Ccmain01().execute();
                    } catch (com.systema.modernized.native_gen.Ccmain01.StopRunException e) {
                        // Clean exit via STOP RUN
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                    return org.springframework.batch.repeat.RepeatStatus.FINISHED;
                }, transactionManager)
                .build();
    }
}