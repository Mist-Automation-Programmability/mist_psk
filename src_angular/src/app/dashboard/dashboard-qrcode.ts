import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

export interface QrcodeData {
    ssid: string;
    passphrase: string
}

@Component({
    selector: 'dashboard-qrcode',
    templateUrl: 'dashboard-qrcode.html',
})
export class QrCodeDialog {
    public qrcode: string = null;

    constructor(
        public dialogRef: MatDialogRef<QrCodeDialog>,
        @Inject(MAT_DIALOG_DATA) public data: QrcodeData) {
        this.qrcode = "WIFI:S:" + data.ssid + ";T:WPA;P:" + data.passphrase + ";;";
    }
    onNoClick(): void {
        this.dialogRef.close();
    }
}



