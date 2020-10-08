import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { ReactiveFormsModule } from '@angular/forms';

import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatStepperModule } from '@angular/material/stepper';
import { MatDividerModule } from '@angular/material/divider';
import { MatCardModule } from '@angular/material/card';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatPaginatorModule } from '@angular/material/paginator';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule } from '@angular/material/dialog'
import { MatIconModule } from '@angular/material/icon';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { QRCodeModule } from 'angularx-qrcode';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { TwoFactorDialog } from './login/login-2FA';
import { DashboardComponent } from './dashboard/dashboard.component';
import { QrCodeDialog } from './dashboard/dashboard-qrcode';
import { DeleteDialog } from './dashboard/dashboard-delete';
import { PskDialog } from './dashboard/dashboard-psk';
import { EmailDialog } from './dashboard/dashboard-email';
import { ErrorDialog } from './dashboard/dashboard-error';
import { WarningDialog } from './dashboard/dashboard-warning';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent, TwoFactorDialog,
    DashboardComponent, QrCodeDialog, DeleteDialog, PskDialog, EmailDialog, ErrorDialog, WarningDialog
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    ReactiveFormsModule,
    FlexLayoutModule,
    HttpClientModule,
    MatButtonModule,
    MatSelectModule,
    MatInputModule,
    MatStepperModule,
    MatDividerModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatTableModule,
    MatCheckboxModule,
    MatProgressBarModule,
    MatTooltipModule,
    MatPaginatorModule,
    QRCodeModule,
    MatDialogModule,
    FormsModule,
    MatIconModule,
    MatSnackBarModule
  ],
  providers: [{
    provide: MatRadioModule,
    useValue: { color: 'accent' },
  }],
  bootstrap: [AppComponent]
})
export class AppModule {
  // Diagnostic only: inspect router configuration
  constructor(router: Router) {
    // Use a custom replacer to display function names in the route configs
    const replacer = (key, value) => (typeof value === 'function') ? value.name : value;
  }
}