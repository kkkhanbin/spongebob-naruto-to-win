import { inject } from '@angular/core';
import { HttpBackend, HttpClient, HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const httpBackend = inject(HttpBackend);
  const rawHttp = new HttpClient(httpBackend);
  const token = authService.getAccessToken();

  if (!token) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      const refreshToken = authService.getRefreshToken();
      const isAuthEndpoint = req.url.includes('/auth/login/') || req.url.includes('/auth/refresh/');

      if (error.status !== 401 || !refreshToken || isAuthEndpoint) {
        if (error.status === 401 && !isAuthEndpoint) {
          authService.logout();
        }
        return throwError(() => error);
      }

      return rawHttp
        .post<{ access: string; refresh?: string }>('http://127.0.0.1:8000/api/auth/refresh/', {
          refresh: refreshToken,
        })
        .pipe(
          switchMap((response) => {
            localStorage.setItem('access_token', response.access);
            if (response.refresh) {
              localStorage.setItem('refresh_token', response.refresh);
            }

            return next(
              req.clone({
                setHeaders: {
                  Authorization: `Bearer ${response.access}`,
                },
              }),
            );
          }),
          catchError((refreshError) => {
            authService.logout();
            return throwError(() => refreshError);
          }),
        );
    }),
  );
};
