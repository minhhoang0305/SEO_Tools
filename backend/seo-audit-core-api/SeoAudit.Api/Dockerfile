FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY seo-audit-core-api/ seo-audit-core-api/
RUN dotnet restore seo-audit-core-api/SeoAudit.Api/SeoAudit.Api.csproj

RUN dotnet publish seo-audit-core-api/SeoAudit.Api/SeoAudit.Api.csproj \
    --configuration Release \
    --output /app/publish \
    --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "SeoAudit.Api.dll"]
