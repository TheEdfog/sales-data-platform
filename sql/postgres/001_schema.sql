drop schema if exists sales cascade;
create schema sales;

create table sales.stores (
    plant text primary key,
    store_name text not null
);

create table sales.promo_types (
    type_id text primary key,
    description text not null
);

create table sales.promos (
    promo_id text not null,
    material text not null,
    type_id text not null references sales.promo_types(type_id),
    discount numeric(18, 2) not null check (discount >= 0),
    primary key (promo_id, material)
);

create table sales.bills_head (
    billnum text primary key,
    plant text not null references sales.stores(plant),
    calday date not null
);

create table sales.bills_item (
    billnum text not null references sales.bills_head(billnum),
    material text not null,
    rpa_sat numeric(18, 2) not null check (rpa_sat >= 0),
    qty bigint not null check (qty > 0),
    primary key (billnum, material)
);

create table sales.traffic (
    plant text not null references sales.stores(plant),
    traffic_date date not null,
    quantity bigint not null check (quantity >= 0),
    primary key (plant, traffic_date)
);

create table sales.coupons (
    coupon_id text primary key,
    plant text not null references sales.stores(plant),
    billnum text not null,
    material text not null,
    promo_id text not null,
    coupon_date date not null,
    foreign key (billnum, material) references sales.bills_item(billnum, material),
    foreign key (promo_id, material) references sales.promos(promo_id, material)
);

