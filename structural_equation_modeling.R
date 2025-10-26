# Structural Equation Modeling (SEM) Script
# Theory of Planned Behavior + Protection Motivation Theory
# Behavioral Intention Dataset Analysis
# Author: Dataset Generator
# Date: 2024

# Load required libraries
if (!require(lavaan)) install.packages("lavaan", dependencies = TRUE)
if (!require(semPlot)) install.packages("semPlot", dependencies = TRUE)
if (!require(dplyr)) install.packages("dplyr", dependencies = TRUE)
if (!require(ggplot2)) install.packages("ggplot2", dependencies = TRUE)
if (!require(corrplot)) install.packages("corrplot", dependencies = TRUE)

library(lavaan)
library(semPlot)
library(dplyr)
library(ggplot2)
library(corrplot)

# Load dataset
data <- read.csv("behavioral_intention_dataset.csv")

cat("=================================================================\n")
cat("STRUCTURAL EQUATION MODELING ANALYSIS\n")
cat("Theory of Planned Behavior + Protection Motivation Theory\n")
cat("=================================================================\n")

# ============================================================================
# MODEL 1: BASIC TPB MODEL (Intention as Outcome)
# ============================================================================

cat("\n--- MODEL 1: BASIC TPB MODEL ---\n")

tpb_model <- '
  # Measurement Model
  ATT =~ ATT1 + ATT2 + ATT3
  SN =~ SN1 + SN2 + SN3
  PBC =~ PBC1 + PBC2 + PBC3
  INT =~ INT1 + INT2 + INT3
  
  # Structural Model - TPB
  INT ~ ATT + SN + PBC + Past_Behavior
'

# Fit TPB model
tpb_fit <- sem(tpb_model, data = data, estimator = "ML")

cat("TPB Model Results:\n")
summary(tpb_fit, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)

# Extract key results
tpb_fit_indices <- fitMeasures(tpb_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
tpb_r2 <- inspect(tpb_fit, "rsquare")

cat("\nTPB Model Fit:\n")
cat("CFI =", round(tpb_fit_indices["cfi"], 3), "\n")
cat("TLI =", round(tpb_fit_indices["tli"], 3), "\n")
cat("RMSEA =", round(tpb_fit_indices["rmsea"], 3), "\n")
cat("SRMR =", round(tpb_fit_indices["srmr"], 3), "\n")
cat("R² (Intention) =", round(tpb_r2["INT"], 3), "\n")

# ============================================================================
# MODEL 2: EXTENDED TPB + PMT MODEL (Intention as Outcome)
# ============================================================================

cat("\n--- MODEL 2: EXTENDED TPB + PMT MODEL ---\n")

extended_model <- '
  # Measurement Model
  ATT =~ ATT1 + ATT2 + ATT3
  SN =~ SN1 + SN2 + SN3
  PBC =~ PBC1 + PBC2 + PBC3
  INT =~ INT1 + INT2 + INT3
  PS =~ PS1 + PS2 + PS3
  PV =~ PV1 + PV2 + PV3
  SE =~ SE1 + SE2 + SE3
  RE =~ RE1 + RE2 + RE3
  
  # Structural Model - Extended TPB + PMT
  INT ~ ATT + SN + PBC + PS + PV + SE + RE + Past_Behavior
  
  # PMT relationships
  PS ~~ PV  # Threat appraisal components can correlate
  SE ~~ RE  # Coping appraisal components can correlate
'

# Fit extended model
extended_fit <- sem(extended_model, data = data, estimator = "ML")

cat("Extended TPB + PMT Model Results:\n")
summary(extended_fit, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)

# Extract key results
extended_fit_indices <- fitMeasures(extended_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
extended_r2 <- inspect(extended_fit, "rsquare")

cat("\nExtended Model Fit:\n")
cat("CFI =", round(extended_fit_indices["cfi"], 3), "\n")
cat("TLI =", round(extended_fit_indices["tli"], 3), "\n")
cat("RMSEA =", round(extended_fit_indices["rmsea"], 3), "\n")
cat("SRMR =", round(extended_fit_indices["srmr"], 3), "\n")
cat("R² (Intention) =", round(extended_r2["INT"], 3), "\n")

# Model comparison
cat("\nModel Comparison (TPB vs Extended):\n")
model_comparison <- anova(tpb_fit, extended_fit)
print(model_comparison)

# ============================================================================
# MODEL 3: FULL LONGITUDINAL MODEL (T2 Behavior as Ultimate Outcome)
# ============================================================================

cat("\n--- MODEL 3: FULL LONGITUDINAL MODEL ---\n")

longitudinal_model <- '
  # Measurement Model
  ATT =~ ATT1 + ATT2 + ATT3
  SN =~ SN1 + SN2 + SN3
  PBC =~ PBC1 + PBC2 + PBC3
  INT =~ INT1 + INT2 + INT3
  PS =~ PS1 + PS2 + PS3
  PV =~ PV1 + PV2 + PV3
  SE =~ SE1 + SE2 + SE3
  RE =~ RE1 + RE2 + RE3
  
  # Structural Model - Full longitudinal
  # Predictors of Intention (T1)
  INT ~ ATT + SN + PBC + PS + PV + SE + RE + Past_Behavior
  
  # Predictors of T2 Behavior
  T2_Actual_Behavior ~ INT + PBC + Past_Behavior + Age + Tech_Comfort
  
  # PMT correlations
  PS ~~ PV
  SE ~~ RE
  
  # Control variable correlations
  Age ~~ Tech_Comfort
'

# Fit longitudinal model
longitudinal_fit <- sem(longitudinal_model, data = data, estimator = "ML")

cat("Full Longitudinal Model Results:\n")
summary(longitudinal_fit, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)

# Extract key results
long_fit_indices <- fitMeasures(longitudinal_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
long_r2 <- inspect(longitudinal_fit, "rsquare")

cat("\nLongitudinal Model Fit:\n")
cat("CFI =", round(long_fit_indices["cfi"], 3), "\n")
cat("TLI =", round(long_fit_indices["tli"], 3), "\n")
cat("RMSEA =", round(long_fit_indices["rmsea"], 3), "\n")
cat("SRMR =", round(long_fit_indices["srmr"], 3), "\n")
cat("R² (Intention) =", round(long_r2["INT"], 3), "\n")
cat("R² (T2 Behavior) =", round(long_r2["T2_Actual_Behavior"], 3), "\n")

# ============================================================================
# MEDIATION ANALYSIS
# ============================================================================

cat("\n=================================================================\n")
cat("MEDIATION ANALYSIS\n")
cat("=================================================================\n")

# Test indirect effects through intention
mediation_model <- '
  # Measurement Model
  ATT =~ ATT1 + ATT2 + ATT3
  SN =~ SN1 + SN2 + SN3
  PBC =~ PBC1 + PBC2 + PBC3
  INT =~ INT1 + INT2 + INT3
  SE =~ SE1 + SE2 + SE3
  
  # Structural paths
  INT ~ a1*ATT + a2*SN + a3*PBC + a4*SE + Past_Behavior
  T2_Actual_Behavior ~ b*INT + c1*ATT + c2*SN + c3*PBC + c4*SE + Past_Behavior
  
  # Indirect effects
  indirect_ATT := a1*b
  indirect_SN := a2*b
  indirect_PBC := a3*b
  indirect_SE := a4*b
  
  # Total effects
  total_ATT := c1 + (a1*b)
  total_SN := c2 + (a2*b)
  total_PBC := c3 + (a3*b)
  total_SE := c4 + (a4*b)
'

# Fit mediation model
mediation_fit <- sem(mediation_model, data = data, estimator = "ML")

cat("Mediation Analysis Results:\n")
summary(mediation_fit, standardized = TRUE)

# Extract indirect effects
indirect_effects <- parameterEstimates(mediation_fit, standardized = TRUE)
indirect_results <- indirect_effects[grepl("indirect_|total_", indirect_effects$label), ]

cat("\nIndirect Effects (through Intention):\n")
print(indirect_results[, c("label", "est", "std.all", "se", "z", "pvalue")])

# ============================================================================
# MODERATION ANALYSIS
# ============================================================================

cat("\n=================================================================\n")
cat("MODERATION ANALYSIS\n")
cat("=================================================================\n")

# Test moderation by demographic variables
# Example: Does age moderate the intention-behavior relationship?

# Create interaction terms
data$INT_mean <- rowMeans(data[, c("INT1", "INT2", "INT3")])
data$Age_centered <- scale(data$Age, center = TRUE, scale = FALSE)[,1]
data$INT_Age_interaction <- data$INT_mean * data$Age_centered

# Moderation model
moderation_model <- '
  T2_Actual_Behavior ~ INT_mean + Age_centered + INT_Age_interaction + Past_Behavior + Tech_Comfort
'

moderation_fit <- sem(moderation_model, data = data, estimator = "ML")

cat("Moderation Analysis (Age moderating Intention-Behavior):\n")
summary(moderation_fit, standardized = TRUE)

# Test significance of interaction
mod_params <- parameterEstimates(moderation_fit)
interaction_effect <- mod_params[mod_params$rhs == "INT_Age_interaction", ]
cat("\nInteraction Effect:\n")
cat("β =", round(interaction_effect$est, 3), 
    ", SE =", round(interaction_effect$se, 3),
    ", p =", round(interaction_effect$pvalue, 3), "\n")

if (interaction_effect$pvalue < 0.05) {
  cat("✓ Significant moderation effect detected\n")
} else {
  cat("⚠ No significant moderation effect\n")
}

# ============================================================================
# MODEL COMPARISON AND SELECTION
# ============================================================================

cat("\n=================================================================\n")
cat("MODEL COMPARISON SUMMARY\n")
cat("=================================================================\n")

# Create comparison table
model_comparison_table <- data.frame(
  Model = c("Basic TPB", "Extended TPB+PMT", "Longitudinal"),
  Chi_square = c(tpb_fit_indices["chisq"], extended_fit_indices["chisq"], long_fit_indices["chisq"]),
  df = c(tpb_fit_indices["df"], extended_fit_indices["df"], long_fit_indices["df"]),
  CFI = c(tpb_fit_indices["cfi"], extended_fit_indices["cfi"], long_fit_indices["cfi"]),
  TLI = c(tpb_fit_indices["tli"], extended_fit_indices["tli"], long_fit_indices["tli"]),
  RMSEA = c(tpb_fit_indices["rmsea"], extended_fit_indices["rmsea"], long_fit_indices["rmsea"]),
  SRMR = c(tpb_fit_indices["srmr"], extended_fit_indices["srmr"], long_fit_indices["srmr"]),
  R2_Intention = c(tpb_r2["INT"], extended_r2["INT"], long_r2["INT"]),
  R2_Behavior = c(NA, NA, long_r2["T2_Actual_Behavior"])
)

cat("Model Fit Comparison:\n")
print(round(model_comparison_table, 3))

# ============================================================================
# EFFECT SIZES AND PRACTICAL SIGNIFICANCE
# ============================================================================

cat("\n=================================================================\n")
cat("EFFECT SIZES AND PRACTICAL SIGNIFICANCE\n")
cat("=================================================================\n")

# Extract standardized coefficients from best model (longitudinal)
std_params <- standardizedSolution(longitudinal_fit)
structural_paths <- std_params[std_params$op == "~", ]

cat("Standardized Path Coefficients (Longitudinal Model):\n")
cat("Path\t\t\tβ\tSE\tp-value\tEffect Size\n")
cat("--------------------------------------------------------\n")

for (i in 1:nrow(structural_paths)) {
  path <- paste(structural_paths$lhs[i], "<-", structural_paths$rhs[i])
  beta <- structural_paths$est.std[i]
  se <- structural_paths$se[i]
  p <- structural_paths$pvalue[i]
  
  # Effect size interpretation (Cohen's conventions)
  effect_size <- ifelse(abs(beta) >= 0.5, "Large",
                       ifelse(abs(beta) >= 0.3, "Medium",
                             ifelse(abs(beta) >= 0.1, "Small", "Negligible")))
  
  cat(sprintf("%-20s\t%.3f\t%.3f\t%.3f\t%s\n", path, beta, se, p, effect_size))
}

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================

cat("\n=================================================================\n")
cat("SAVING RESULTS\n")
cat("=================================================================\n")

# Save model comparison
write.csv(model_comparison_table, "sem_model_comparison.csv", row.names = FALSE)
cat("✓ Model comparison saved to: sem_model_comparison.csv\n")

# Save path coefficients
write.csv(structural_paths, "structural_path_coefficients.csv", row.names = FALSE)
cat("✓ Path coefficients saved to: structural_path_coefficients.csv\n")

# Save indirect effects
write.csv(indirect_results, "mediation_effects.csv", row.names = FALSE)
cat("✓ Mediation effects saved to: mediation_effects.csv\n")

# Save R-squared values
r2_results <- data.frame(
  Outcome = names(long_r2),
  R_squared = as.numeric(long_r2)
)
write.csv(r2_results, "r_squared_values.csv", row.names = FALSE)
cat("✓ R-squared values saved to: r_squared_values.csv\n")

# Create path diagrams
tryCatch({
  # Longitudinal model diagram
  png("longitudinal_model_diagram.png", width = 1400, height = 1000)
  semPaths(longitudinal_fit, what = "std", layout = "tree2",
           edge.label.cex = 0.7, node.label.cex = 0.7,
           title = "Full Longitudinal Model - Standardized Coefficients",
           rotation = 2)
  dev.off()
  cat("✓ Longitudinal model diagram saved to: longitudinal_model_diagram.png\n")
  
  # Mediation model diagram
  png("mediation_model_diagram.png", width = 1200, height = 800)
  semPaths(mediation_fit, what = "std", layout = "tree2",
           edge.label.cex = 0.8, node.label.cex = 0.8,
           title = "Mediation Model - Standardized Coefficients")
  dev.off()
  cat("✓ Mediation model diagram saved to: mediation_model_diagram.png\n")
  
}, error = function(e) {
  cat("⚠ Could not create path diagrams\n")
})

# ============================================================================
# RESEARCH IMPLICATIONS
# ============================================================================

cat("\n=================================================================\n")
cat("RESEARCH IMPLICATIONS AND CONCLUSIONS\n")
cat("=================================================================\n")

cat("Key Findings:\n")
cat("1. Intention Prediction:\n")
cat("   - R² =", round(long_r2["INT"], 3), "- explains", round(long_r2["INT"]*100, 1), "% of intention variance\n")

cat("2. Behavior Prediction:\n")
cat("   - R² =", round(long_r2["T2_Actual_Behavior"], 3), "- explains", round(long_r2["T2_Actual_Behavior"]*100, 1), "% of behavior variance\n")

# Identify strongest predictors
intention_predictors <- structural_paths[structural_paths$lhs == "INT", ]
behavior_predictors <- structural_paths[structural_paths$lhs == "T2_Actual_Behavior", ]

strongest_int_predictor <- intention_predictors[which.max(abs(intention_predictors$est.std)), ]
strongest_beh_predictor <- behavior_predictors[which.max(abs(behavior_predictors$est.std)), ]

cat("3. Strongest Predictors:\n")
cat("   - Intention:", strongest_int_predictor$rhs, "(β =", round(strongest_int_predictor$est.std, 3), ")\n")
cat("   - Behavior:", strongest_beh_predictor$rhs, "(β =", round(strongest_beh_predictor$est.std, 3), ")\n")

cat("\n4. Theoretical Implications:\n")
if (long_r2["INT"] > 0.5) {
  cat("   ✓ Strong support for TPB + PMT in predicting intentions\n")
} else {
  cat("   ⚠ Moderate support for theoretical model\n")
}

if (long_r2["T2_Actual_Behavior"] > 0.3) {
  cat("   ✓ Good prediction of actual behavior\n")
} else {
  cat("   ⚠ Intention-behavior gap evident\n")
}

cat("\n5. Practical Implications:\n")
cat("   - Focus interventions on strongest predictors\n")
cat("   - Consider habit/past behavior in behavior change programs\n")
cat("   - Address both cognitive and motivational factors\n")

cat("\n=================================================================\n")
cat("STRUCTURAL EQUATION MODELING ANALYSIS COMPLETE\n")
cat("=================================================================\n")
cat("All results saved to CSV files and diagrams created.\n")
cat("Dataset successfully analyzed using advanced SEM techniques.\n")