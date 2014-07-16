#
# End-to-end testing of Choosing Wisely Alert
#                  EHR sends message to Maven...currently we are approximating this message with test_ehr_   XML files
#                                               Maven back-end client converts to FHIR message
#                                               FHIR message is evaluated against Choosing Wisely alerts using SQL function *EVALRULES*
#
#                 Step 1       *EVALRULES*   testing
#
#                 Step 2       *EHR message" order-->Maven;  confirm Alert-->EHR 
#
echo "Testing Maven backend...confirming Choosing Wisely Rule -- AAO 1...findable by Maven function EvalRules"
echo " "
 sudo su postgres -c "psql -f step_1_evalRulesAssert.sql -d maven -e -o  $MAVEN_ROOT/endToEndTesting/alerts_evidence/step_1_evalRulesAssert.output"
echo " "
echo "**** confirm step1_evalRulesAssert.output -- 8 test cases are all True ******"
cat $MAVEN_ROOT/endToEndTesting/alerts_evidence/step_1_evalRulesAssert.output

