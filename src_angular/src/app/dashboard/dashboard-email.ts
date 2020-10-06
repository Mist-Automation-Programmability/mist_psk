import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder } from '@angular/forms';

export interface PskElement {
    id: string;
    name: string;
    ssid: string;
    vlan_id: number;
    created_by: string;
    created_time: number;
    modified_time: number;
    passphrase: string;
    user_email: string;
}

@Component({
    selector: 'dashboard-email',
    templateUrl: 'dashboard-email.html',
})
export class EmailDialog {
    frmEmail = this.formBuilder.group({
        name: [this.data.name || ""],// Validators.required],
        user_email: [this.data.user_email || ""]
    });

    constructor(
        public dialogRef: MatDialogRef<EmailDialog>,
        @Inject(MAT_DIALOG_DATA) public data: PskElement, private formBuilder: FormBuilder
    ) { }


    confirm() {
        this.dialogRef.close({ user_email: this.frmEmail.value.user_email, name: this.frmEmail.value.name })
    }
    cancel(): void {
        this.dialogRef.close();
    }

}
