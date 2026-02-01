-- Association Rules Model Storage

create table if not exists association_rules (
    id uuid primary key default gen_random_uuid(),

    -- Rule definition
    antecedent text[] not null,
    consequent text[] not null,

    -- Rule metrics
    support double precision not null,
    confidence double precision not null,
    lift double precision not null,
    leverage double precision not null,
    conviction double precision not null,

    -- Model metadata
    model_version text not null,
    trained_at timestamptz not null default now(),

    -- Optional scope (future-proofing)
    scope text default 'order', -- 'order' | 'customer'
    
    constraint antecedent_not_empty check (array_length(antecedent, 1) > 0),
    constraint consequent_not_empty check (array_length(consequent, 1) > 0)
);

-- Helpful indexes for fast recommendations
create index if not exists idx_assoc_rules_antecedent
    on association_rules using gin (antecedent);

create index if not exists idx_assoc_rules_scope
    on association_rules (scope);

create index if not exists idx_assoc_rules_version
    on association_rules (model_version);
