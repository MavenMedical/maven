 sudo su postgres -c "psql -f step_1_evalRulesAssert.sql -d maven -e -o  $MAVEN_ROOT/endToEndTesting/alerts_evidence/step_1_evalRulesAssert.output"

