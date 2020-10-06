import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConnectorService {
  private headersSource = new BehaviorSubject({});
  private cookiesSource = new BehaviorSubject({});
  private hostSource = new BehaviorSubject('');
  private selfSource = new BehaviorSubject({});

  headers = this.headersSource.asObservable();
  host = this.hostSource.asObservable();
  cookies = this.cookiesSource.asObservable();
  self = this.selfSource.asObservable();

  constructor() { }

  headersSet(data: {}) {
    this.headersSource.next(data)
  }
  cookiesSet(data: {}) {
    this.cookiesSource.next(data)
  }
  hostSet(data: string) {
    this.hostSource.next(data)
  }
  selfSet(data: {}) {
    this.selfSource.next(data)
  }
}
