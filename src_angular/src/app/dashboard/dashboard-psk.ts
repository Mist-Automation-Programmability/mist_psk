import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, Validators } from '@angular/forms';


@Component({
    selector: 'dashboard-psk',
    templateUrl: 'dashboard-psk.html',
})

export class PskDialog {
    frmPsk = this.formBuilder.group({
        id: [this.data.psk.id],
        name: [this.data.psk.name, Validators.required],
        psk: [this.data.psk.passphrase, [Validators.minLength(8), Validators.maxLength(63)]],
        ssid: [this.data.psk.ssid, Validators.required],
        vlan_id: [this.data.psk.vlan_id, [Validators.min(1), Validators.max(4095)]],
        user_email: [this.data.psk.user_email, Validators.email],
        renewable: [false]
    });
    renewable = false;
    editing = this.data.editing;

    constructor(public dialogRef: MatDialogRef<PskDialog>, @Inject(MAT_DIALOG_DATA) public data, private formBuilder: FormBuilder) { }

    confirm() {
        this.dialogRef.close(this.frmPsk.value)
    }
    cancel(): void {
        this.dialogRef.close();
    }

    changeRenewable(){
        this.renewable = this.frmPsk.value.renewable;
        if (this.renewable){this.frmPsk.controls["psk"].setValue("********")}
        else {this.frmPsk.controls["psk"].setValue("")}
    }

    generatePsk() {
        let possible = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        let text = "";
        for (let i = 0; i < 12; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        this.frmPsk.controls["psk"].setValue(text);
    }
}