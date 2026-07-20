create schema if not exists sales;

create table sales.stores (
    plant text not null,
    store_name text not null
) distributed replicated;

create table sales.promo_types (
    type_id text not null,
    description text not null
) distributed replicated;

create table sales.promos (
    promo_id text not null,
    material text not null,
    type_id text not null,
    discount numeric(18, 2) not null
) distributed replicated;

create table sales.bills_head (
    billnum text not null,
    plant text not null,
    calday date not null
)
with (appendoptimized=true, orientation=column, compresstype=zstd)
distributed by (billnum)
partition by range (calday)
(start (date '2021-01-01') inclusive end (date '2022-01-01') exclusive every (interval '1 month'));

create table sales.bills_item (
    billnum text not null,
    material text not null,
    rpa_sat numeric(18, 2) not null,
    qty bigint not null
)
with (appendoptimized=true, orientation=column, compresstype=zstd)
distributed by (billnum);

create table sales.traffic (
    plant text not null,
    traffic_date date not null,
    quantity bigint not null
)
with (appendoptimized=true, orientation=column, compresstype=zstd)
distributed by (plant)
partition by range (traffic_date)
(start (date '2021-01-01') inclusive end (date '2022-01-01') exclusive every (interval '1 month'));

create table sales.coupons (
    coupon_id text not null,
    plant text not null,
    billnum text not null,
    material text not null,
    promo_id text not null,
    coupon_date date not null
)
with (appendoptimized=true, orientation=column, compresstype=zstd)
distributed by (billnum)
partition by range (coupon_date)
(start (date '2021-01-01') inclusive end (date '2022-01-01') exclusive every (interval '1 month'));

