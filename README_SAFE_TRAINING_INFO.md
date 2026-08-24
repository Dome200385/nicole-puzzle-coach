SAFE TRAINING INFO PATCH

Based on the last fully working build before the regression.

Important:
- No global helper depends on a locally scoped variable.
- Median and unsolved lists cannot fail because optional extra information is missing.
- Existing data rendering remains the source of truth.

Changes:
- Median Top 5: Last time, MSP median, gap, calculated gap %, Coach.
- Repeats: Coach moved full-width under the metrics.
- Unsolved: reads difficulty from difficulty_label or existing msp_insights fields;
  reads prediction from prediction or existing msp_prediction fields.
- If MSP has no value, displays "–" and Coach explains that MSP currently has no value.
- Skip / restore unchanged.
