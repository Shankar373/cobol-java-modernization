package com.systema.modernized.domain;

import java.math.BigDecimal;

public class Policy {

    private String policyId;
    private String customerId;
    private String type;
    private String status;
    private String currency;
    private BigDecimal coverLimit;
    private BigDecimal deductible;
    private Integer effectiveDate;
    private Integer expiryDate;
    private String reserved;

    public String getPolicyId() { return policyId; }
    public void setPolicyId(String val) { this.policyId = val; }

    public String getCustomerId() { return customerId; }
    public void setCustomerId(String val) { this.customerId = val; }

    public String getType() { return type; }
    public void setType(String val) { this.type = val; }

    public String getStatus() { return status; }
    public void setStatus(String val) { this.status = val; }

    public String getCurrency() { return currency; }
    public void setCurrency(String val) { this.currency = val; }

    public BigDecimal getCoverLimit() { return coverLimit; }
    public void setCoverLimit(BigDecimal val) { this.coverLimit = val; }

    public BigDecimal getDeductible() { return deductible; }
    public void setDeductible(BigDecimal val) { this.deductible = val; }

    public Integer getEffectiveDate() { return effectiveDate; }
    public void setEffectiveDate(Integer val) { this.effectiveDate = val; }

    public Integer getExpiryDate() { return expiryDate; }
    public void setExpiryDate(Integer val) { this.expiryDate = val; }

    public String getReserved() { return reserved; }
    public void setReserved(String val) { this.reserved = val; }

}