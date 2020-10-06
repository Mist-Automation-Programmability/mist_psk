import { Component, OnInit, Inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormBuilder } from '@angular/forms';
import { ConnectorService } from '../connector.service';

export interface TwoFactorData {
  twoFactor: string;
}

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})


export class LoginComponent implements OnInit {

  constructor(private formBuilder: FormBuilder, private http: HttpClient, private router: Router, private appService: ConnectorService, public dialog: MatDialog) { }

  host = null;
  headers = {};
  cookies = {};
  self = {};
  loading: boolean;
  hosts = [
    { value: 'api.mist.com', viewValue: 'US - manage.mist.com' },
    { value: 'api.eu.mist.com', viewValue: 'EU - manage.eu.mist.com' },
    { value: 'api.gc1.mist.com', viewValue: 'GCP - manage.gc1.mist.com' }
  ];

  frmStepLogin = this.formBuilder.group({
    host: [''],
    credentials: this.formBuilder.group({
      email: [''],
      password: [''],
    }),
    token: [''],
  });
  error_mess = {
    "username": "",
    "token": ""
  }
  //// INIT ////
  ngOnInit() {
    this.frmStepLogin = this.formBuilder.group({
      host: ['api.mist.com'],
      credentials: this.formBuilder.group({
        email: [''],
        password: [''],
      }),
      token: [""],
    });
  }

  //// COMMON ////
  check_host() {
    if (this.frmStepLogin.value.host != '') {
      return true;
    } else {
      return false;
    }
  }

  reset_response() {
    this.host = null;
    this.appService.headersSet({});
    this.appService.cookiesSet({});
    this.appService.selfSet({});
    this.appService.hostSet(this.host);
    this.reset_error_mess();
  }
  reset_error_mess(){
    this.error_mess = {
      "username": "",
      "token": ""
    }
  }

  parse_response(data) {
    if ("error" in data) {
      this.loading = false;
      this.error_mess["username"] = data.error;
    } else if ("data" in data) {
      if ("detail" in data.data) {
        this.loading = false;
        this.error_mess[data["method"]] = data.data.detail;
      } else if ("two_factor_required" in data.data && "two_factor_passed" in data.data) {
        if (data.data["two_factor_required"] == false) {
          this.authenticated(data)
        } else if (data.data["two_factor_passed"] == true) {
          this.authenticated(data)
        } else {
          this.open2FA()
        }
      } else {
        this.authenticated(data)
      }
    }
  }

  authenticated(data) {
    this.appService.headersSet(data.headers);
    this.appService.cookiesSet(data.cookies);
    this.appService.hostSet(this.host);
    this.appService.selfSet(data.data)
    this.loading = false; this.router.navigate(['/dashboard']);
  }

  //// AUTHENTICATION ////
  submitCredentials() {
    this.reset_response();
    this.host = this.frmStepLogin.value.host;
    if (this.check_host()) {
      this.loading = true;
      this.http.post<any>('/api/login/', { host: this.frmStepLogin.value.host, email: this.frmStepLogin.value.credentials.email, password: this.frmStepLogin.value.credentials.password }).subscribe({
        next: data => this.parse_response(data),
        error: error => console.error('There was an error!', error)
      })
    }
  }
  submitToken() {
    this.reset_response();
    this.host = this.frmStepLogin.value.host;
    if (this.check_host()) {
      this.loading = true;
      this.http.post<any>('/api/login/', { host: this.frmStepLogin.value.host, token: this.frmStepLogin.value.token }).subscribe({
        next: data => this.parse_response(data),
        error: error => console.error('There was an error!', error)
      })

    }
  }
  submit2FA(twoFactor) {
    this.host = this.frmStepLogin.value.host;
    if (this.check_host()) {
      this.loading = true;
      this.http.post<any>('/api/login/', { host: this.frmStepLogin.value.host, email: this.frmStepLogin.value.credentials.email, password: this.frmStepLogin.value.credentials.password, two_factor: twoFactor }).subscribe({
        next: data => this.parse_response(data),
        error: error => console.error('There was an error!', error)
      })
    }
  }

  //// DIALOG BOX ////
  open2FA(): void {
    const dialogRef = this.dialog.open(TwoFactorDialog, {});
    dialogRef.afterClosed().subscribe(result => {
      this.submit2FA(result)
    });
  }
}



//// 2FA /////

@Component({
  selector: 'login-2fa',
  templateUrl: 'login-2fa.html',
})
export class TwoFactorDialog {
  public twoFactor: string;
  constructor(public dialogRef: MatDialogRef<TwoFactorDialog>) { }

  close2FA() {
    this.dialogRef.close(this.twoFactor);
  }
  cancel2FA(): void {
    this.dialogRef.close();
  }
}