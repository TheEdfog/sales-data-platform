with gross_sales as (
    select
        bh.plant,
        sum(bi.rpa_sat) as gross_revenue,
        sum(bi.qty) as sold_quantity,
        count(distinct bh.billnum) as bills_count
    from sales.bills_head as bh
    join sales.bills_item as bi on bi.billnum = bh.billnum
    group by bh.plant
),
coupon_candidates as (
    select
        c.coupon_id,
        c.plant,
        p.type_id,
        p.discount,
        bi.rpa_sat,
        bi.qty,
        row_number() over (partition by c.coupon_id order by bi.billnum, bi.material) as row_number
    from sales.coupons as c
    join sales.bills_item as bi
      on bi.billnum = c.billnum
     and bi.material = c.material
    join sales.promos as p
      on p.promo_id = c.promo_id
     and p.material = c.material
),
promo_totals as (
    select
        plant,
        sum(
            case
                when type_id = '001' then discount
                when type_id = '002' then rpa_sat / nullif(qty, 0) * discount / 100.0
                else 0
            end
        ) as discount
    from coupon_candidates
    where row_number = 1
    group by plant
),
traffic_totals as (
    select plant, sum(quantity) as traffic
    from sales.traffic
    group by plant
),
coupon_totals as (
    select plant, count(distinct coupon_id) as promo_sold
    from sales.coupons
    group by plant
)
select
    stores.plant,
    stores.store_name,
    round(coalesce(gross_sales.gross_revenue, 0), 2) as gross_revenue,
    round(coalesce(promo_totals.discount, 0), 2) as discount,
    round(coalesce(gross_sales.gross_revenue, 0) - coalesce(promo_totals.discount, 0), 2)
        as net_revenue,
    coalesce(gross_sales.sold_quantity, 0) as sold_quantity,
    coalesce(gross_sales.bills_count, 0) as bills_count,
    coalesce(traffic_totals.traffic, 0) as traffic,
    coalesce(coupon_totals.promo_sold, 0) as promo_sold,
    round(
        case when coalesce(gross_sales.sold_quantity, 0) = 0 then 0
             else coalesce(coupon_totals.promo_sold, 0) * 100.0 / gross_sales.sold_quantity end,
        2
    ) as promo_rate_pct,
    round(
        case when coalesce(gross_sales.bills_count, 0) = 0 then 0
             else gross_sales.sold_quantity * 1.0 / gross_sales.bills_count end,
        2
    ) as avg_items_per_bill,
    round(
        case when coalesce(traffic_totals.traffic, 0) = 0 then 0
             else coalesce(gross_sales.bills_count, 0) * 100.0 / traffic_totals.traffic end,
        2
    ) as conversion_rate_pct,
    round(
        case when coalesce(gross_sales.bills_count, 0) = 0 then 0
             else gross_sales.gross_revenue / gross_sales.bills_count end,
        2
    ) as avg_bill_amount,
    round(
        case when coalesce(traffic_totals.traffic, 0) = 0 then 0
             else coalesce(gross_sales.gross_revenue, 0) / traffic_totals.traffic end,
        2
    ) as revenue_per_visitor
from sales.stores as stores
left join gross_sales on gross_sales.plant = stores.plant
left join promo_totals on promo_totals.plant = stores.plant
left join traffic_totals on traffic_totals.plant = stores.plant
left join coupon_totals on coupon_totals.plant = stores.plant
order by stores.plant

