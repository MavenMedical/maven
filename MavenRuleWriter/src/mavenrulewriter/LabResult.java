/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package mavenrulewriter;

import javax.swing.ListModel;

/**
 *
 * @author Efisch
 */
public class LabResult extends javax.swing.JFrame implements ConditionFrame {

    /**
     * Creates new form EncounterDiagnosis
     */
    MavenRuleFrontend myParent; 
    LabResultDetail editTarget;
    public LabResult(MavenRuleFrontend parent) {
        initComponents();
        myParent = parent;
    }
    public LabResult(MavenRuleFrontend parent, LabResultDetail editTarget) {
        initComponents();
        myParent = parent;
        this.editTarget=editTarget;
        ListModel m = LabDataSelector.getModel();
        for (int c =0;c<m.getSize();c++){
            if (m.getElementAt(c).toString().equals(editTarget.getType())){
                LabDataSelector.setSelectedIndex(c);
            }
        }
        m = LabValueRelation.getModel();
        for (int c =0;c<m.getSize();c++){
            if (m.getElementAt(c).toString().equals(editTarget.getRelation())){
                LabValueRelation.setSelectedIndex(c);
            }
        }
        LabResultValue.setText(editTarget.getValue());

                
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        OKButton = new javax.swing.JButton();
        jButton2 = new javax.swing.JButton();
        EncounterProcedureTypeLabel = new javax.swing.JLabel();
        jLabel1 = new javax.swing.JLabel();
        LabDataSelector = new javax.swing.JComboBox();
        jLabel2 = new javax.swing.JLabel();
        LabValueRelation = new javax.swing.JComboBox();
        LabResultValue = new javax.swing.JTextField();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);

        OKButton.setText("OK");
        OKButton.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                OKButtonActionPerformed(evt);
            }
        });

        jButton2.setText("Cancel");
        jButton2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton2ActionPerformed(evt);
            }
        });

        EncounterProcedureTypeLabel.setText("Follow Rule only if ");

        jLabel1.setFont(new java.awt.Font("Tahoma", 0, 24)); // NOI18N
        jLabel1.setText("Create New Lab Result Criterion");

        LabDataSelector.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Lipid Panel: LDL", "Lipid Panel: HDL" }));

        jLabel2.setText("Has a Result");

        LabValueRelation.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Less Than", "Greater Than", "Equal To" }));

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(120, 120, 120)
                        .addComponent(jLabel1, javax.swing.GroupLayout.PREFERRED_SIZE, 501, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(layout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(EncounterProcedureTypeLabel)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(LabDataSelector, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(32, 32, 32)
                        .addComponent(jLabel2)
                        .addGap(38, 38, 38)
                        .addComponent(LabValueRelation, javax.swing.GroupLayout.PREFERRED_SIZE, 123, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(LabResultValue, javax.swing.GroupLayout.PREFERRED_SIZE, 128, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(layout.createSequentialGroup()
                        .addGap(277, 277, 277)
                        .addComponent(OKButton, javax.swing.GroupLayout.PREFERRED_SIZE, 78, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jButton2, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap(58, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGap(28, 28, 28)
                .addComponent(jLabel1)
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(EncounterProcedureTypeLabel)
                    .addComponent(LabDataSelector, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel2)
                    .addComponent(LabValueRelation, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(LabResultValue, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 43, Short.MAX_VALUE)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(OKButton)
                    .addComponent(jButton2))
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void OKButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_OKButtonActionPerformed
        Detail n = getDetail();
        if (editTarget!=null){
            n.name = editTarget.name;
        }
        
        myParent.recieveDetail(n);
        this.dispose();
    }//GEN-LAST:event_OKButtonActionPerformed

    private void jButton2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton2ActionPerformed
        this.myParent.setEnabled(true);
        this.dispose();       
    }//GEN-LAST:event_jButton2ActionPerformed
    public Detail getDetail(){
            LabResultDetail result = new LabResultDetail("");
            result.setRelation(this.LabValueRelation.getSelectedItem().toString());
            result.setType(this.LabDataSelector.getSelectedItem().toString());
            result.setValue(this.LabResultValue.getText());
            return result;
    }
    /**
     * @param args the command line arguments
     */
   

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel EncounterProcedureTypeLabel;
    private javax.swing.JComboBox LabDataSelector;
    private javax.swing.JTextField LabResultValue;
    private javax.swing.JComboBox LabValueRelation;
    private javax.swing.JButton OKButton;
    private javax.swing.JButton jButton2;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    // End of variables declaration//GEN-END:variables

    
  
}