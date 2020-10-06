import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

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
    selector: 'dashboard-delete',
    templateUrl: 'dashboard-delete.html',
})
export class DeleteDialog {

    constructor(
        public dialogRef: MatDialogRef<DeleteDialog>,
        @Inject(MAT_DIALOG_DATA) public data: PskElement
    ) { }

    confirm(psk_id) {
        this.dialogRef.close(psk_id)
    }
    cancel(): void {
        this.dialogRef.close();
    }

}