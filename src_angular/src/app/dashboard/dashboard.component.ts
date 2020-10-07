import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';

import { MatPaginator } from '@angular/material/paginator';
import { merge, Observable, of as observableOf } from 'rxjs';
import { catchError, map, startWith, switchMap } from 'rxjs/operators';

import { QrCodeDialog } from './dashboard-qrcode';
import { DeleteDialog } from './dashboard-delete';
import { PskDialog } from './dashboard-psk';
import { EmailDialog } from './dashboard-email';
import { ErrorDialog } from './dashboard-error';


import { ConnectorService } from '../connector.service';
import { MatTableDataSource } from '@angular/material/table';


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

  loadPsks(body: {}, pageIndex: number, pageSize: number): Observable<MistPsks> {
    body["page"] = pageIndex;
    body["limit"] = pageSize;
    return this._httpClient.post<MistPsks>('/api/psks/', body);
  }
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
  sitegroups_ids: string[] = [];
  ssid: string = "";
  me: string = "";

  sitesDisabled: boolean = true;
  wlansDisabled: boolean = true;
  createDisabled: boolean = true;

  topBarLoading = false;
  loading = false;

  isRateLimitReached = false;
  pskDatabase: MistHttpDatabase | null;
  filteredPskDatase: MatTableDataSource<PskElement> | null;
  psks: PskElement[] = []

  filters_enabled: boolean = false
  resultsLength = 50;
  displayedColumns: string[] = ['name', 'user_email', 'ssid', 'vlan_id', 'created_by', 'created_time', 'modified_time', 'action'];

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
      this.orgs = this.sortList(this.orgs, "name");
      if (this.orgs.length == 1) {
        this.org_id = this.orgs[1]["id"]
      }
    }
  }


  getPsks() {
    var body = null
    if (this.site_id == "org") {
      body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id, ssid: this.ssid, full: this.filters_enabled }
    } else if (this.site_id) {
      body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, ssid: this.ssid, full: this.filters_enabled }
    }
    if (body) {
      
      if (this.filters_enabled) {
        this.loading = true;
        this.http.post<PskElement[]>('/api/psks/', body).subscribe({
          next: data => {
            this.filteredPskDatase = new MatTableDataSource(data["results"]);
            this.filteredPskDatase.paginator = this.paginator;
            this.loading = false;
          },
          error: error => {
            var message: string = "There was an error... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })

      } else {
        this.pskDatabase = new MistHttpDatabase(this.http);
        merge(this.paginator.page, this.paginator.pageSize)
          .pipe(
            startWith({}),
            switchMap(() => {
              this.loading = true;
              return this.pskDatabase!.loadPsks(body, this.paginator.pageIndex, this.paginator.pageSize);
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
    if (data.sites.length > 0) {
      this.sites = this.sortList(data.sites, "name");
    }
    this.sitesDisabled = false;
    this.topBarLoading = false;
  }
  parseWlans(data) {
    this.wlans = []
    if (data.wlans.length > 0) {
      this.wlans = this.sortList(data.wlans, "ssid");
      this.getPsks()
    }
    this.wlansDisabled = false;
    this.topBarLoading = false;
  }

  changeOrg() {
    this.topBarLoading = true;
    this.http.post<any>('/api/sites/', { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id }).subscribe({
      next: data => this.parseSites(data),
      error: error => {
        var message: string = "There was an error... "
        if ("error" in error) {
          message += error["error"]["message"]
        }
        this.topBarLoading = false;
        this.openError(message)
      }
    })
  }
  changeSite() {
    this.topBarLoading = true;
    var body = null
    this.createDisabled = false;
    this.sitegroups_ids = [];
    if (this.site_id == "org") {
      body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id }
    } else if (this.site_id) {
      this.sites.forEach(site => {
        if (site.id == this.site_id) {
          this.sitegroups_ids = site.sitegroups_ids;
        }
      })
      body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, sitegroups_ids: this.sitegroups_ids, org_id: this.org_id }
    }
    if (body) {
      this.http.post<any>('/api/wlans/', body).subscribe({
        next: data => this.parseWlans(data),
        error: error => {
          var message: string = "There was an error... "
          if ("error" in error) { message += error["error"]["message"] }
          this.topBarLoading = false;
          this.openError(message)
        }
      })
    }
  }
  changeWlan() {
    this.getPsks()
  }


  // COMMON
  sortList(data, attribute) {
    return data.sort(function (a, b) {
      var nameA = a[attribute].toUpperCase(); // ignore upper and lowercase
      var nameB = b[attribute].toUpperCase(); // ignore upper and lowercase
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
    this.filteredPskDatase.filter = filterValue.trim().toLowerCase();

    if (this.filteredPskDatase.paginator) {
      this.filteredPskDatase.paginator.firstPage();
    }
  }


  // DIALOG BOXES
  // ERROR
  openError(message): void {
    const dialogRef = this.dialog.open(ErrorDialog, {
      data: message
    });
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
        var body = null;
        if (this.site_id == "org") {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }
        } else if (this.site_id) {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }
        }
        this.http.post<any>('/api/psks/create/', body).subscribe({
          next: data => this.getPsks(),
          error: error => {
            var message: string = "There was an error... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    })
  }
  // EDIT PSK
  openEdit(psk: PskElement): void {
    const dialogRef = this.dialog.open(PskDialog, {
      data: { wlans: this.wlans, psk: psk, editing: true }
    })
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        var body = null;
        if (this.site_id == "org") {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id, id: result.id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }
        } else if (this.site_id) {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, id: result.id, user_email: result.user_email, name: result.name, passphrase: result.psk, ssid: result.ssid, vlan_id: result.vlan_id, created_by: this.me }
        }
        this.http.post<any>('/api/psks/create/', body).subscribe({
          next: data => this.getPsks(),
          error: error => {
            var message: string = "There was an error... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
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
        var body = null;
        if (this.site_id == "org") {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id, psk_id: psk.id }
        } else if (this.site_id) {
          body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, psk_id: psk.id }
        }
        this.http.post<any>('/api/psks/delete/', body).subscribe({
          next: data => this.getPsks(),
          error: error => {
            var message: string = "There was an error... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
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
          error: error => {
            var message: string = "There was an error... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    });
  }
}

