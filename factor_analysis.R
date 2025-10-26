# Confirmatory Factor Analysis Script
# Behavioral Intention Dataset - TPB and PMT Constructs
# Author: Dataset Generator
# Date: 2024

# Load required libraries
if (!require(lavaan)) install.packages("lavaan", dependencies = TRUE)
if (!require(semPlot)) install.packages("semPlot", dependencies = TRUE)
if (!require(psych)) install.packages("psych", dependencies = TRUE)
if (!require(corrplot)) install.packages("corrplot", dependencies = TRUE)
if (!require(dplyr)) install.packages("dplyr", dependencies = TRUE)

library(lavaan)
library(semPlot)
library(psych)
library(corrplot)
library(dplyr)

# Load dataset
data <- read.csv("behavioral_intention_dataset.csv")

# ============================================================================
# EXPLORATORY FACTOR ANALYSIS (EFA) - Initial Exploration
# ============================================================================

cat("=================================================================\n")
cat("EXPLORATORY FACTOR ANALYSIS\n")
cat("=================================================================\n")

# Select all construct items for EFA
construct_items <- c(
  # TPB constructs
  "ATT1", "ATT2", "ATT3",
  "SN1", "SN2", "SN3", 
  "PBC1", "PBC2", "PBC3",
  "INT1", "INT2", "INT3",
  # PMT constructs
  "PS1", "PS2", "PS3",
  "PV1", "PV2", "PV3",
  "SE1", "SE2", "SE3",
  "RE1", "RE2", "RE3"
)

# Subset data for EFA
efa_data <- data[, construct_items]

# Check data suitability for factor analysis
kmo_result <- KMO(efa_data)
cat("Kaiser-Meyer-Olkin (KMO) Test:\n")
cat("Overall KMO =", round(kmo_result$MSA, 3), "\n")
if (kmo_result$MSA > 0.8) {
  cat("✓ Excellent sampling adequacy\n")
} else if (kmo_result$MSA > 0.7) {
  cat("✓ Good sampling adequacy\n")
} else {
  cat("⚠ Marginal sampling adequacy\n")
}

# Bartlett's test of sphericity
bartlett_result <- cortest.bartlett(efa_data)
cat("\nBartlett's Test of Sphericity:\n")
cat("Chi-square =", round(bartlett_result$chisq, 2), "\n")
cat("p-value =", format(bartlett_result$p.value, scientific = TRUE), "\n")
if (bartlett_result$p.value < 0.001) {
  cat("✓ Significant - Factor analysis appropriate\n")
}

# Determine number of factors
cat("\nFactor Extraction Methods:\n")
# Parallel analysis
pa_result <- fa.parallel(efa_data, fm = "ml", fa = "fa", n.iter = 100)
cat("Parallel Analysis suggests:", pa_result$nfact, "factors\n")

# Scree plot would be generated here (visual inspection)
# For this analysis, we expect 8 factors based on theory

# Run EFA with 8 factors (theoretical expectation)
efa_8 <- fa(efa_data, nfactors = 8, rotate = "oblimin", fm = "ml")

cat("\nEFA Results (8 factors, oblimin rotation):\n")
print(efa_8$loadings, cutoff = 0.3, sort = TRUE)

# ============================================================================
# CONFIRMATORY FACTOR ANALYSIS (CFA) - Measurement Model
# ============================================================================

cat("\n=================================================================\n")
cat("CONFIRMATORY FACTOR ANALYSIS - MEASUREMENT MODEL\n")
cat("=================================================================\n")

# Define the measurement model
measurement_model <- '
  # TPB Constructs
  ATT =~ ATT1 + ATT2 + ATT3
  SN =~ SN1 + SN2 + SN3
  PBC =~ PBC1 + PBC2 + PBC3
  INT =~ INT1 + INT2 + INT3
  
  # PMT Constructs
  PS =~ PS1 + PS2 + PS3
  PV =~ PV1 + PV2 + PV3
  SE =~ SE1 + SE2 + SE3
  RE =~ RE1 + RE2 + RE3
'

# Fit the measurement model
cfa_fit <- cfa(measurement_model, data = data, estimator = "ML")

# Model fit summary
cat("CFA Model Fit Summary:\n")
summary(cfa_fit, fit.measures = TRUE, standardized = TRUE)

# Extract fit indices
fit_indices <- fitMeasures(cfa_fit, c("chisq", "df", "pvalue", "cfi", "tli", 
                                     "rmsea", "rmsea.ci.lower", "rmsea.ci.upper", 
                                     "srmr", "aic", "bic"))

cat("\nKey Fit Indices:\n")
cat("Chi-square =", round(fit_indices["chisq"], 2), "\n")
cat("df =", fit_indices["df"], "\n")
cat("p-value =", round(fit_indices["pvalue"], 4), "\n")
cat("CFI =", round(fit_indices["cfi"], 3), 
    ifelse(fit_indices["cfi"] >= 0.95, " ✓ Excellent", 
           ifelse(fit_indices["cfi"] >= 0.90, " ✓ Acceptable", " ⚠ Poor")), "\n")
cat("TLI =", round(fit_indices["tli"], 3),
    ifelse(fit_indices["tli"] >= 0.95, " ✓ Excellent", 
           ifelse(fit_indices["tli"] >= 0.90, " ✓ Acceptable", " ⚠ Poor")), "\n")
cat("RMSEA =", round(fit_indices["rmsea"], 3), 
    " [", round(fit_indices["rmsea.ci.lower"], 3), ", ", 
    round(fit_indices["rmsea.ci.upper"], 3), "]",
    ifelse(fit_indices["rmsea"] <= 0.06, " ✓ Excellent", 
           ifelse(fit_indices["rmsea"] <= 0.08, " ✓ Acceptable", " ⚠ Poor")), "\n")
cat("SRMR =", round(fit_indices["srmr"], 3),
    ifelse(fit_indices["srmr"] <= 0.08, " ✓ Good", " ⚠ Poor"), "\n")

# Factor loadings
cat("\nStandardized Factor Loadings:\n")
loadings <- standardizedSolution(cfa_fit)
loadings_items <- loadings[loadings$op == "=~", ]
print(loadings_items[, c("lhs", "rhs", "est.std", "pvalue")])

# Check for loadings < 0.7
weak_loadings <- loadings_items[loadings_items$est.std < 0.7, ]
if (nrow(weak_loadings) > 0) {
  cat("\n⚠ Items with loadings < 0.7:\n")
  print(weak_loadings[, c("lhs", "rhs", "est.std")])
} else {
  cat("\n✓ All factor loadings ≥ 0.7\n")
}

# ============================================================================
# RELIABILITY AND VALIDITY ANALYSIS
# ============================================================================

cat("\n=================================================================\n")
cat("RELIABILITY AND VALIDITY ANALYSIS\n")
cat("=================================================================\n")

# Calculate reliability for each construct
constructs <- list(
  ATT = c("ATT1", "ATT2", "ATT3"),
  SN = c("SN1", "SN2", "SN3"),
  PBC = c("PBC1", "PBC2", "PBC3"),
  INT = c("INT1", "INT2", "INT3"),
  PS = c("PS1", "PS2", "PS3"),
  PV = c("PV1", "PV2", "PV3"),
  SE = c("SE1", "SE2", "SE3"),
  RE = c("RE1", "RE2", "RE3")
)

cat("Construct Reliability:\n")
cat("Construct\tCronbach α\tComposite Reliability\tAVE\n")
cat("--------------------------------------------------------\n")

reliability_results <- data.frame(
  Construct = character(),
  Cronbach_Alpha = numeric(),
  Composite_Reliability = numeric(),
  AVE = numeric(),
  stringsAsFactors = FALSE
)

for (construct_name in names(constructs)) {
  items <- constructs[[construct_name]]
  construct_data <- data[, items]
  
  # Cronbach's Alpha
  alpha <- psych::alpha(construct_data)$total$raw_alpha
  
  # Extract loadings for this construct
  construct_loadings <- loadings_items[loadings_items$lhs == construct_name, "est.std"]
  
  # Composite Reliability
  sum_loadings <- sum(construct_loadings)
  sum_loadings_sq <- sum(construct_loadings^2)
  error_variance <- length(construct_loadings) - sum_loadings_sq
  cr <- sum_loadings^2 / (sum_loadings^2 + error_variance)
  
  # Average Variance Extracted (AVE)
  ave <- sum_loadings_sq / length(construct_loadings)
  
  cat(sprintf("%s\t\t%.3f\t\t%.3f\t\t\t%.3f\n", construct_name, alpha, cr, ave))
  
  reliability_results <- rbind(reliability_results, 
                              data.frame(Construct = construct_name,
                                       Cronbach_Alpha = alpha,
                                       Composite_Reliability = cr,
                                       AVE = ave))
}

# Discriminant validity (Fornell-Larcker criterion)
cat("\nDiscriminant Validity (Fornell-Larcker Criterion):\n")
cat("Square root of AVE should be > correlations with other constructs\n")

# Calculate construct correlations
construct_scores <- data.frame(
  ATT = rowMeans(data[, constructs$ATT]),
  SN = rowMeans(data[, constructs$SN]),
  PBC = rowMeans(data[, constructs$PBC]),
  INT = rowMeans(data[, constructs$INT]),
  PS = rowMeans(data[, constructs$PS]),
  PV = rowMeans(data[, constructs$PV]),
  SE = rowMeans(data[, constructs$SE]),
  RE = rowMeans(data[, constructs$RE])
)

construct_correlations <- cor(construct_scores)
cat("\nConstruct Correlation Matrix:\n")
print(round(construct_correlations, 3))

# Check discriminant validity
cat("\nDiscriminant Validity Check:\n")
for (i in 1:nrow(reliability_results)) {
  construct <- reliability_results$Construct[i]
  sqrt_ave <- sqrt(reliability_results$AVE[i])
  max_corr <- max(abs(construct_correlations[construct, -which(colnames(construct_correlations) == construct)]))
  
  status <- ifelse(sqrt_ave > max_corr, "✓", "⚠")
  cat(sprintf("%s: √AVE = %.3f, Max |r| = %.3f %s\n", construct, sqrt_ave, max_corr, status))
}

# ============================================================================
# MODEL MODIFICATION (if needed)
# ============================================================================

cat("\n=================================================================\n")
cat("MODEL MODIFICATION INDICES\n")
cat("=================================================================\n")

# Modification indices
mod_indices <- modificationIndices(cfa_fit, sort. = TRUE, maximum.number = 10)
cat("Top 10 Modification Indices:\n")
print(mod_indices[1:10, ])

if (max(mod_indices$mi) > 10) {
  cat("\n⚠ Large modification indices detected (MI > 10)\n")
  cat("Consider model modifications, but ensure theoretical justification\n")
} else {
  cat("\n✓ No major model modifications needed (all MI ≤ 10)\n")
}

# ============================================================================
# SAVE RESULTS
# ============================================================================

cat("\n=================================================================\n")
cat("SAVING RESULTS\n")
cat("=================================================================\n")

# Save reliability results
write.csv(reliability_results, "construct_reliability_results.csv", row.names = FALSE)
cat("✓ Reliability results saved to: construct_reliability_results.csv\n")

# Save construct correlations
write.csv(construct_correlations, "construct_correlations.csv")
cat("✓ Construct correlations saved to: construct_correlations.csv\n")

# Save fit indices
fit_indices_df <- data.frame(
  Index = names(fit_indices),
  Value = as.numeric(fit_indices)
)
write.csv(fit_indices_df, "cfa_fit_indices.csv", row.names = FALSE)
cat("✓ CFA fit indices saved to: cfa_fit_indices.csv\n")

# Save factor loadings
loadings_df <- loadings_items[, c("lhs", "rhs", "est.std", "se", "z", "pvalue")]
colnames(loadings_df) <- c("Factor", "Item", "Loading", "SE", "Z_value", "P_value")
write.csv(loadings_df, "factor_loadings.csv", row.names = FALSE)
cat("✓ Factor loadings saved to: factor_loadings.csv\n")

# Create path diagram (if semPlot is available)
tryCatch({
  png("measurement_model_diagram.png", width = 1200, height = 800)
  semPaths(cfa_fit, what = "std", layout = "tree2", 
           edge.label.cex = 0.8, node.label.cex = 0.8,
           title = "Measurement Model - Standardized Loadings")
  dev.off()
  cat("✓ Path diagram saved to: measurement_model_diagram.png\n")
}, error = function(e) {
  cat("⚠ Could not create path diagram\n")
})

cat("\n=================================================================\n")
cat("FACTOR ANALYSIS COMPLETE\n")
cat("=================================================================\n")
cat("Summary:\n")
cat("✓ EFA conducted to explore factor structure\n")
cat("✓ CFA conducted to test measurement model\n")
cat("✓ Reliability and validity assessed\n")
cat("✓ Results saved to CSV files\n")
cat("\nNext steps: Run structural equation modeling (SEM) analysis\n")