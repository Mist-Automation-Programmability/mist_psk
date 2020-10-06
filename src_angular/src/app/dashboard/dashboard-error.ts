import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
    selector: 'dashboard-error',
    templateUrl: 'dashboard-error.html',
})
export class ErrorDialog {

    constructor(
        public dialogRef: MatDialogRef<ErrorDialog>,
        @Inject(MAT_DIALOG_DATA) public data: string
    ) { }

    ok(): void {
        this.dialogRef.close();
    }

}