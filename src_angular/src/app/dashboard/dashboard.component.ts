import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { Router } from "@angular/router";

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
import { MatSnackBar, MatSnackBarHorizontalPosition, MatSnackBarVerticalPosition } from '@angular/material/snack-bar';
import { WarningDialog } from './dashboard-warning';

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
  expire_time: number;
  max_usage: number,
  "-max_usage": boolean
}

export interface VlanCheckElement {
  wlan_id: string,
  reason: string,
  vlan_id: number,
  scope_name: string,
  scope_id: string,
  code: string
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
  styleUrls: ['./dashboard.component.scss']
})


export class DashboardComponent implements OnInit {


  headers = {};
  cookies = {};
  host = '';
  self = {};
  search = "";
  current_org = {"name": ""};
  current_msp = {"name": ""};
  msps = [];
  msp_orgs = {};
  orgs = [];
  sites = [];
  scope: string;
  wlans = [];
  msp_id: string = "";
  org_id: string = "";
  site_id: string = "";
  sitegroups_ids: string[] = [];
  default_expire_time: number = null;
  psk_length: number = 12;
  ssid: string = "";
  me: string = "";
  now: number;

  orgsHidden: boolean = true;
  sitesHidden: boolean = true;
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
  resultsLength = 0;
  displayedColumns: string[] = ['status', 'name', 'user_email', 'ssid', 'vlan_id', 'created_by', 'expire_time', 'action'];

  @ViewChild(MatPaginator) paginator: MatPaginator;

  constructor(private _http: HttpClient, private _appService: ConnectorService, public _dialog: MatDialog, private _snackBar: MatSnackBar, private _router: Router) { }

  ngOnInit() {

    this._appService.headers.subscribe(headers => this.headers = headers)
    this._appService.cookies.subscribe(cookies => this.cookies = cookies)
    this._appService.host.subscribe(host => this.host = host)
    this._appService.self.subscribe(self => this.self = self || {})

    if (this.self["email"]){
      this.me = this.self["email"];
    } else if (this.self["name"]) {
      this.me = this.self["name"];
    } else {
      this.me = null;
    }
    this.getConfig()
    if (!this.me) this._router.navigateByUrl("/")
    if (Object.keys(this.self).length > 0 && this.self["privileges"]) {
      this.parsePrivileges();
    }
  }

  parsePrivileges(): void {
    this.msps = [];
    this.orgs = [];
    this.psks = [];
    this.msp_orgs = {};
    var tmp_orgs: string[] = [];
    this.self["privileges"].forEach(element => {

      // process MSP privilege
      if (element["scope"] == "msp") {
        this.msps.push({ id: element["msp_id"], name: element["name"], role: element["role"] });
      }

      // process ORG privilege
      else if (element["scope"] == "org") {
        // if the ORG belong to an MSP, store is in the msp_orgs dict (if not already in it)
        if (element.hasOwnProperty("msp_id")) {
          if (!this.msp_orgs.hasOwnProperty(element["org_id"])) {
            this.msp_orgs[element["org_id"]] = { msp_id: element["msp_id"], id: element["org_id"], name: element["name"], scope: "org", role: element["role"] };
          }
        }
        // if the ORG doesn't belong to an MSP, store it in the orgs array (if not already in it)
        else if (tmp_orgs.indexOf(element["org_id"]) < 0) {
          this.orgs.push({ id: element["org_id"], name: element["name"], scope: "org", role: element["role"] });
          tmp_orgs.push(element["org_id"]);
        }
      } 
      
      // process SITE privilege
      else if (element["scope"] == "site") {
        // if the SITE belong to an MSP, store is in the msp_orgs dict (if not already in it)
        if (element.hasOwnProperty("msp_id")) {
          if (!this.msp_orgs.hasOwnProperty(element["org_id"])) {
            this.msp_orgs[element["org_id"]] = { id: element["org_id"], name: element["org_name"], scope: "site", role: element["role"] };
          }
        }
        // if the SITE doesn't belong to an MSP, store it in the orgs array (if not already in it)
        else if (tmp_orgs.indexOf(element["org_id"]) < 0) {
          this.orgs.push({ id: element["org_id"], name: element["org_name"], scope: "site", role: element["role"] });
          tmp_orgs.push(element["org_id"]);
        }
      }
    });

    // find the orphan MSP ORGs (orgs belonging to an MSP, but MSP not in the list)
    // put back the org in the org array
    for (var org_id in this.msp_orgs){
      var org = this.msp_orgs[org_id];
      var org_msp_id = org["msp_id"];
      var msp = this.msps.find((msp) => msp["id"] == org_msp_id);
      if (!msp){
        this.orgs.push(org);
      }
    }
    
    if (this.msps.length == 0 && this.orgs.length == 1) {
      this.current_org = this.orgs[0]
      this.orgsHidden = true;
      this.changeOrg();
    } else {
      this.msps = this.sortList(this.msps, "name");
      this.orgs = this.sortList(this.orgs, "name");
      this.orgsHidden = false;
    }
  }

  //////////////////////////////////////////////////
  // CONFIG
  parsePskConfig(data): void {
    if (data.psk_length) {
      this.psk_length = data.psk_length
    }
    if (data.default_expire_time) {
      this.default_expire_time = data.default_expire_time
    }
  }

  getConfig() {
    this._http.get<PskElement[]>('/api/psks/config').subscribe({
      next: data => this.parsePskConfig(data),
      error: error => {
        var message: string = "There was an error... "
        if ("error" in error) { message += error["error"]["message"] }
        this.openError(message)
      }
    })
  }

  //////////////////////////////////////////////////
  // PSK
  getPsks() {
    this.now = Math.trunc(Date.now() / 1000);
    var body = null
    if (this.site_id == "org") {
      body = { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id, ssid: this.ssid, full: this.filters_enabled }
    } else if (this.site_id) {
      body = { host: this.host, cookies: this.cookies, headers: this.headers, site_id: this.site_id, ssid: this.ssid, full: this.filters_enabled }
    }
    if (body) {

      if (this.filters_enabled) {
        this.loading = true;
        this._http.post<PskElement[]>('/api/psks/', body).subscribe({
          next: data => {
            this.filteredPskDatase = new MatTableDataSource(data["results"]);
            this.filteredPskDatase.filterPredicate = (psk: PskElement, filter: string) => {
              if (psk.name.toLowerCase().includes(filter.toLowerCase())) { return true; }
              if (psk.created_by && psk.created_by.toLowerCase().includes(filter.toLowerCase())) { return true; }
              if (psk.user_email && psk.user_email.toLowerCase().includes(filter.toLowerCase())) { return true; }
              if (psk.ssid.toLowerCase().includes(filter.toLowerCase())) { return true; }
              //if (psk.role.toLowerCase() == filter.toLowerCase()) {return true;}
              return false;
            };
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
        this.pskDatabase = new MistHttpDatabase(this._http);
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

  //////////////////////////////////////////////////
  // WLANS

  changeWlan() {
    this.psks = [];
    this.getPsks()
  }

  parseWlans(data) {
    this.wlans = []
    if (data.wlans.length == 1) {
      this.wlans = data.wlans;
      this.ssid = this.wlans[0].ssid;
      this.getPsks();
    }
    else if (data.wlans.length > 0) {
      this.wlans = this.sortList(data.wlans, "ssid");
      this.getPsks()
    }
    this.wlansDisabled = false;
    this.topBarLoading = false;
  }


  //////////////////////////////////////////////////
  // SITES

  changeSite() {
    this.psks = [];
    this.topBarLoading = true;
    var body = null
    this.createDisabled = false;
    this.sitegroups_ids = [];
    if (this.site_id == "org") {
      body = {
        host: this.host,
        cookies: this.cookies,
        headers: this.headers,
        org_id: this.org_id
      }
    } else if (this.site_id) {
      this.sites.forEach(site => {
        if (site.id == this.site_id) {
          this.sitegroups_ids = site.sitegroups_ids;
        }
      })
      body = {
        host: this.host,
        cookies: this.cookies,
        headers: this.headers,
        site_id: this.site_id,
        sitegroups_ids: this.sitegroups_ids,
        org_id: this.org_id
      }
    }
    if (body) {
      this._http.post<any>('/api/wlans/', body).subscribe({
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

  parseSites(data) {
    if (data.sites.length > 0) {
      this.sites = this.sortList(data.sites, "name");
    }
    this.sitesDisabled = false;
    this.topBarLoading = false;
    if (this.sites.length == 1) {
      this.site_id = this.sites[0].id;
    }
    if (this.scope != "org" && this.sites.length == 1) {
      this.sitesDisabled = true
      this.changeSite();
    }
  }


  //////////////////////////////////////////////////
  // MSPS
  parseOrgs(orgs: []): void {
    this.psks = [];
    this.orgs = [];
    var tmp_orgs: string[] = [];
    orgs.forEach(element => {
      var role = undefined;
      if (tmp_orgs.indexOf(element["org_id"]) < 0) {
        if (this.msp_orgs.hasOwnProperty(element["id"])) role = this.msp_orgs[element["id"]]["role"]
        else role = this.current_msp["role"];
        this.orgs.push({ id: element["id"], name: element["name"], scope: "org", role: role });
        tmp_orgs.push(element["id"]);
      }
    });
    if (this.orgs.length == 1) {
      this.current_org = this.orgs[0]
      this.changeOrg();
    } else {
      this.orgs = this.sortList(this.orgs, "name");
    }
  }

  changeMsp() {
    console.log(this.current_msp)
    this.sitesDisabled = true;
    this.createDisabled = true;
    this.current_org = {"name": ""};
    this.site_id = undefined;
    this.orgs = [];
    this.sites = [];
    this.wlansDisabled = true;
    this.wlans = [];
    this.msp_id = this.current_msp["id"]
    this.scope = undefined
    if (this.msp_id) {
      this.topBarLoading = true;
      this._http.post<any>('/api/orgs/', { host: this.host, cookies: this.cookies, headers: this.headers, msp_id: this.msp_id }).subscribe({
        next: data => {
          if ("orgs" in data) this.parseOrgs(data["orgs"]);
          else this.orgs = [];
          this.topBarLoading = false;
        },
        error: error => {
          var message: string = "There was an error... "
          if ("error" in error) {
            message += error["error"]["message"]
          }
          this.topBarLoading = false;
          this.openError(message)
        }
      })
    } else this.parsePrivileges();
  }
  //////////////////////////////////////////////////
  // ORGS

  changeOrg() {
    this.psks = [];
    this.topBarLoading = true;
    this.sitesDisabled = true;
    this.createDisabled = true;
    this.sites = [];
    this.site_id = undefined;
    this.wlansDisabled = true;
    this.wlans = [];
    this.org_id = this.current_org["id"]
    this.scope = this.current_org["scope"]

    if (this.scope == "org") {
      this._http.post<any>('/api/sites/', { host: this.host, cookies: this.cookies, headers: this.headers, org_id: this.org_id }).subscribe({
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
    } else {
      let data = { sites: [] }
      this.self["privileges"].forEach(privilege => {
        if (privilege["org_id"] == this.org_id) {
          data.sites.push({ name: privilege["name"], id: privilege["site_id"] })
        }
      })
      this.parseSites(data)
    }
  }



  //////////////////////////////////////////////////
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
    //this.filteredPskDatase.filter = filterValue.trim().toLowerCase();
    this.filteredPskDatase.filter = filterValue;

    if (this.filteredPskDatase.paginator) {
      this.filteredPskDatase.paginator.firstPage();
    }
  }


  // DIALOG BOXES
  // ERROR
  openError(message: string): void {
    const dialogRef = this._dialog.open(ErrorDialog, {
      data: message
    });
  }
  // Warning VLAN
  checkVlan(data): void {
    if ("vlan_check" in data && data["vlan_check"].length > 0) {
      var bigWarning: boolean = false
      if (data["vlan_check"].length == 1) {
        var message = "VLAN misconfiguration has been detected for this SSID. This may prevent the user to connect."
      } else {
        var message = "VLAN misconfiguration has been detected in " + data["vlan_check"].length + " templates. This may prevent the user to connect."
      }
      data["vlan_check"].forEach(element => {
        console.log(element["code"])
        if (["untagged", "vlan_pooling_disabled", "static_vlan"].indexOf(element["code"]) >= 0) {
          bigWarning = true
          console.log(bigWarning)
        }
      })
      this.openWarningVlan(message, data["vlan_check"], bigWarning)
    }
  }

  openWarningVlan(message: string, vlan_check: VlanCheckElement[], bigWarning: boolean): void {
    const dialogRef = this._dialog.open(WarningDialog, {
      data: { text: message, vlan_check: vlan_check, bigWarning: bigWarning },
      height: 'auto',
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this._http.post<any>('/api/vlans/', { host: this.host, cookies: this.cookies, headers: this.headers, vlan_check: vlan_check }).subscribe({
          next: data => {
            if (data["error"].length == 0) {
              this.openSnackBar("VLAN configuration successfully updated", "Done")
            } else {

            }

          },
          error: error => {
            var message: string = "Unable to update VLAN configuration... "
            if ("error" in error) {
              message += error["error"]["message"]
            }
            this.openError(message)
          }
        })
      }
    })
  }

  // QRCODE DIALOG
  openQrcode(psk: PskElement): void {
    const dialogRef = this._dialog.open(QrCodeDialog, {
      data: { ssid: psk.ssid, passphrase: psk.passphrase }
    });
  }




  // CREATE DIALOG
  openCreate(): void {
    let expire_time = null;
    if (this.default_expire_time) {
      expire_time = Date.now() + this.default_expire_time * 3600000;
    }
    var newPsk: PskElement = {
      id: null,
      name: "",
      vlan_id: null,
      ssid: this.ssid,
      passphrase: "",
      expire_time: expire_time,
      created_by: this.me,
      created_time: null,
      modified_time: null,
      user_email: null,
      max_usage: 0,
      "-max_usage": true
    };
    const dialogRef = this._dialog.open(PskDialog, {
      data: { 
        wlans: this.wlans,
        psk: newPsk,
        editing: false,
        default_expire_time: this.default_expire_time,
        psk_length:this.psk_length
      }
    })
    dialogRef.afterClosed().subscribe(result => {
      console.log(result);
      if (result) {
        var body = {
          host: this.host,
          cookies: this.cookies,
          headers: this.headers,
          org_id: this.org_id,
          user_email: result.user_email,
          name: result.name,
          passphrase: result.psk,
          expire_time: result.expire_time,
          ssid: result.ssid,
          vlan_id: result.vlan_id,
          created_by: this.me,
          renewable: result.renewable
        }
        if (this.site_id == "org") {
          body["org_id"]= this.org_id;
        } else if (this.site_id) {
          body["site_id"]= this.site_id;
        }
        if (result.max_usage > 0 && result["-max_usage"]==false){
          body["max_usage"] = result.max_usage;
        } else {
          body["-max_usage"] = true;
        }
        this._http.post<any>('/api/psks/create/', body).subscribe({
          next: data => {
            this.getPsks()
            this.openSnackBar("PSK " + result.name + " successfully created", "Done")
            this.checkVlan(data)
          },
          error: error => {
            var message: string = "Unable to create PSK " + result.name + "... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    })
  }
  // EDIT PSK
  openEdit(psk: PskElement): void {
    const dialogRef = this._dialog.open(PskDialog, {
      data: {
        wlans: this.wlans,
        psk: psk,
        editing: true,
        default_expire_time: this.default_expire_time,
        psk_length: this.psk_length
      }
    })
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        var body = {
          host: this.host,
          cookies: this.cookies,
          headers: this.headers,
          org_id: this.org_id,
          id: result.id,
          user_email: result.user_email,
          name: result.name,
          passphrase: result.psk,
          expire_time: result.expire_time,
          ssid: result.ssid,
          vlan_id: result.vlan_id,
          created_by: this.me,
          renewable: result.renewable
        }
        if (this.site_id == "org") {
          body["org_id"]= this.org_id;
        } else if (this.site_id) {
          body["site_id"]= this.site_id;
        }
        if (result.max_usage > 0 && result["-max_usage"]==false){
          body["max_usage"] = result.max_usage;
        } else {
          body["-max_usage"] = true;
        }
        this._http.post<any>('/api/psks/create/', body).subscribe({
          next: data => {
            this.getPsks()
            this.openSnackBar("PSK " + result.name + " successfully updated", "Done")
            this.checkVlan(data)
          },
          error: error => {
            var message: string = "Unable to save changes to PSK " + psk.name + "... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    })
  }

  // DELETE DIALOG
  openDelete(psk: PskElement): void {
    const dialogRef = this._dialog.open(DeleteDialog, {
      data: psk
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        var body = {
          host: this.host,
          cookies: this.cookies,
          headers: this.headers,
          psk_id: psk.id
        };
        if (this.site_id == "org") {
          body["org_id"]= this.org_id;
        } else if (this.site_id) {
          body["site_id"]= this.site_id;
        }
        this._http.post<any>('/api/psks/delete/', body).subscribe({
          next: data => {
            this.getPsks()
            this.openSnackBar("PSK " + psk.name + " successfully deleted", "Done")
          },
          error: error => {
            var message: string = "Unable to delete the PSK" + psk.name + "... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    });
  }
  // EMAIL DIALOG
  openEmail(psk: PskElement): void {
    const dialogRef = this._dialog.open(EmailDialog, {
      data: psk
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this._http.post<any>('/api/psks/email/', { name: result.name, user_email: result.user_email, psk: psk.passphrase, ssid: psk.ssid, expire_time: psk.expire_time }).subscribe({
          next: data => {
            this.openSnackBar("Email sent to" + psk.user_email, "Done")
          },
          error: error => {
            var message: string = "Unable to send the email to " + result.user_email + "... "
            if ("error" in error) { message += error["error"]["message"] }
            this.openError(message)
          }
        })
      }
    });
  }

  // SNACK BAR
  openSnackBar(message: string, action: string) {
    this._snackBar.open(message, action, {
      duration: 5000,
      horizontalPosition: "center",
      verticalPosition: "top",
    });
  }
}

