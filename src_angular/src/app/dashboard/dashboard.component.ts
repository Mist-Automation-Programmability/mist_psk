import { Component, OnInit, ViewChild, Inject } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, Validators } from '@angular/forms';

import { MatPaginator } from '@angular/material/paginator';
import { merge, Observable, of as observableOf } from 'rxjs';
import { catchError, map, startWith, switchMap } from 'rxjs/operators';

import { ConnectorService } from '../connector.service';


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
export interface MistPsks {
  results: PskElement[];
  total: number;
  limiit: number;
  page: number;
}
export class MistHttpDatabase {
  constructor(private _httpClient: HttpClient) { }

  getPsks(host: string, cookies: {}, headers: {}, site_id: string, ssid: string, page: number, limit: number): Observable<MistPsks> {
    return this._httpClient.post<MistPsks>('/api/psks/', { host: host, cookies: cookies, headers: headers, site_id: site_id, ssid: ssid, page: page, limit: limit });
  }
}

export interface QrcodeData {
  ssid: string;
  passphrase: string
}
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})


export class DashboardComponent implements OnInit {


  headers = {};
  cookies = {};
  host = '';
  self = {};
  search = "";
  orgs = [];
  sites = [];
  wlans = [];
  org_id: string = "";
  site_id: string = "";
  ssid: string = "";
  sitesDisabled: boolean = true;
  wlansDisabled: boolean = true;
  createDisabled: boolean = true;
  me: string = "";
  filters_enabled: boolean = false
  resultsLength = 50;
  loading = false;
  isRateLimitReached = false;
  pskDatabase: MistHttpDatabase | null;

  displayedColumns: string[] = ['name', 'user_email', 'ssid', 'vlan_id', 'created_by', 'created_time', 'modified_time', 'action'];
  psks: PskElement[] = [];
  psks_loaded: PskElement[] = [];
  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(private http: HttpClient, private appService: ConnectorService, public dialog: MatDialog) { }

  ngOnInit() {
    this.appService.headers.subscribe(headers => this.headers = headers)
    this.appService.cookies.subscribe(cookies => this.cookies = cookies)
    this.appService.host.subscribe(host => this.host = host)
    this.appService.self.subscribe(self => this.self = self || {})
    this.me = this.self["email"] || null
    if (this.self != {} && this.self["privileges"]) {
      this.self["privileges"].forEach(element => {
        if (element["scope"] == "org") {
          if (this.orgs.indexOf({ id: element["org_id"], name: element["name"] }) < 0) {
            this.orgs.push({ id: element["org_id"], name: element["name"] })
          }
        } else if (element["scope"] == "site") {
          if (this.orgs.indexOf({ id: element["org_id"], name: element["org_name"] }) < 0) {
            this.orgs.push({ id: element["org_id"], name: element["org_name"] })
          }
        }
      });
      this.orgs = this.sortList(this.orgs);
      if (this.orgs.length == 1) {
        this.org_id = this.orgs[1]["id"]
      }
    }
  }


  getPsks() {
    if (this.site_id) {
      this.psks = []
      if (this.filters_enabled) {
        this.loading = true;
        this.http.post<PskElement[]>('/api/psks/', { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, ssid: this.ssid, full: this.filters_enabled }).subscribe({
          next: data => {
            this.psks_loaded = data["results"];
            this.psks = data["results"];
            this.loading = false;
          },
          error: error => console.error('There was an error!', error)
        })
      } else {
        this.pskDatabase = new MistHttpDatabase(this.http);

        merge(this.paginator.page, this.paginator.pageSize)
          .pipe(
            startWith({}),
            switchMap(() => {
              this.loading = true;
              return this.pskDatabase!.getPsks(
                this.host, this.cookies, this.headers, this.site_id, this.ssid, this.paginator.pageIndex, this.paginator.pageSize);
            }),
            map(data => {
              // Flip flag to show that loading has finished.
              this.loading = false;
              this.isRateLimitReached = false;
              this.resultsLength = data.total;

              return data.results;
            }),
            catchError(() => {
              // Catch if the GitHub API has reached its rate limit. Return empty data.
              this.isRateLimitReached = true;
              return observableOf([]);
            })
          ).subscribe(data => this.psks = data);
      }
    }
  }


  parseSites(data) {
    if (data.data.length > 0) {
      this.sites = this.sortList(data.data);
      if (this.sites.length == 1) {
        this.site_id = this.sites[1]["id"]
      }
    }
  }
  parseWlans(data) {
    if (data.data.length > 0) {
      this.wlans = this.sortList(data.data);
      this.getPsks()
    }
  }

  changeOrg() {
    this.sitesDisabled = false;
    this.http.post<any>('/api/sites/', { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id }).subscribe({
      next: data => this.parseSites(data),
      error: error => console.error('There was an error!', error)
    })
  }
  changeSite() {
    this.wlansDisabled = false;
    this.createDisabled = false;
    this.http.post<any>('/api/wlans/', { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id }).subscribe({
      next: data => this.parseWlans(data),
      error: error => console.error('There was an error!', error)
    })
  }
  changeWlan() {
    this.getPsks()
  }

  // QRCODE DIALOG
  openQrcode(psk: PskElement): void {
    const dialogRef = this.dialog.open(QrCodeDialog, {
      data: { ssid: psk.ssid, passphrase: psk.passphrase }
    });
  }

  // CREATE DIALOG
  openCreate(): void {
    var newPsk: PskElement = {
      id: null,
      name: "",
      vlan_id: null,
      ssid: this.ssid,
      passphrase: "",
      created_by: this.me,
      created_time: null,
      modified_time: null,
      user_email: null
    };
    const dialogRef = this.dialog.open(PskDialog, {
      data: { wlans: this.wlans, psk: newPsk, editing: false }
    })
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.post<any>('/api/psks/create/', { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }).subscribe({
          next: data => this.getPsks(),
          error: error => console.error('There was an error!', error)
        })

      }
    })
  }
  openEdit(psk: PskElement): void {
    const dialogRef = this.dialog.open(PskDialog, {
      data: { wlans: this.wlans, psk: psk, editing: true }
    })
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.post<any>('/api/psks/create/', { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, id: result.id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }).subscribe({
          next: data => this.getPsks(),
          error: error => console.error('There was an error!', error)
        })

      }
    })
  }

  // DELETE DIALOG
  openDelete(psk: PskElement): void {
    const dialogRef = this.dialog.open(DeleteDialog, {
      data: psk
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.post<any>('/api/psks/delete/', { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, psk_id: psk.id }).subscribe({
          next: data => this.getPsks(),
          error: error => console.error('There was an error!', error)
        })

      }
    });
  }
  // EMAIL DIALOG
  openEmail(psk: PskElement): void {
    const dialogRef = this.dialog.open(EmailDialog, {
      data: psk
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.http.post<any>('/api/psks/email/', { name: result.name, user_email: result.user_email, psk: psk.passphrase, ssid: psk.ssid }).subscribe({
          next: data => console.log("done"),
          error: error => console.error('There was an error!', error)
        })

      }
    });
  }
  // COMMON
  sortList(data) {
    return data.sort(function (a, b) {
      var nameA = a["name"].toUpperCase(); // ignore upper and lowercase
      var nameB = b["name"].toUpperCase(); // ignore upper and lowercase
      if (nameA < nameB) {
        return -1;
      }
      if (nameA > nameB) {
        return 1;
      }
      return 0;
    })
  }
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value.trim().toLowerCase();
    if (filterValue == "") { this.psks = this.psks_loaded }
    else {
      this.psks = [];
      this.psks_loaded.forEach(psk => {
        if (psk.name.toLowerCase().indexOf(filterValue) >= 0) { this.psks.push(psk) }
        else if (psk.created_by && psk.created_by.toLowerCase().indexOf(filterValue) >= 0) { this.psks.push(psk) }
      })
    }
  }
}



// QRCODE
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

// Delete
@Component({
  selector: 'dashboard-psk',
  templateUrl: 'dashboard-psk.html',
})

export class PskDialog {
  frmPsk = this.formBuilder.group({
    id: [this.data.psk.id],
    name: [this.data.psk.name],// Validators.required],
    psk: [this.data.psk.passphrase],// Validators.required, Validators.minLength(8), Validators.maxLength(63)],
    ssid: [this.data.psk.ssid],// Validators.required],
    vlan_id: [this.data.psk.vlan_id],// Validators.min(1), Validators.max(4095)]
    user_email: [this.data.psk.user_email]
  });
  editing = this.data.editing;
  constructor(public dialogRef: MatDialogRef<PskDialog>, @Inject(MAT_DIALOG_DATA) public data, private formBuilder: FormBuilder) { }

  confirm() {
    this.dialogRef.close(this.frmPsk.value)
  }
  cancel(): void {
    this.dialogRef.close();
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

// Delete
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
// Email
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
    this.dialogRef.close({ user_email: this.frmEmail.value.user_email, name: this.frmEmail.value.name})
  }
  cancel(): void {
    this.dialogRef.close();
  }

}