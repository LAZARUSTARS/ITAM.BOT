create table if not exists telegram_users(
    id BIGINT primary key,
    first_name text not null,
    username text,
    last_name text,
    language_code text,
    is_premium bool,
    is_admin bool
);
create table if not exists coworking(
    id serial primary key,
    status text not null,
    responsible_id BIGINT not null references telegram_users(id),
    duration integer default null,
    created_at timestamp not null default NOW()
);
create table if not exists profiles(
    user_id BIGINT primary key references telegram_users(id) on delete cascade,
    fio text,
    email text,
    educational_group text,
    portfolio_link text,
    majors text [],
    external_links text [],
    skills text [],
    mentor boolean,
    company text
);
create table if not exists subscriptions(
    id BIGINT primary key references telegram_users(id) on delete cascade,
    coworking boolean default false,
    hack_club boolean default false,
    design_club boolean default false,
    gamedev_club boolean default false,
    ai_club boolean default false,
    robot_club boolean default false,
    itam_digest boolean default false
);
create table if not exists clubs(
    id serial primary key,
    name text not null,
    description text not null,
    chat_link text not null,
    created_at timestamp not null default NOW()
);
create table if not exists admin_invite_codes(
    id serial primary key,
    code text,
    rights_ids BIGINT [] not null,
    admin_id BIGINT not null REFERENCES telegram_users(id) on DELETE CASCADE,
    user_id BIGINT REFERENCES telegram_users(id) on DELETE CASCADE,
    created_at TIMESTAMP WITH TIME zone not null default CURRENT_TIMESTAMP,
    activated_at TIMESTAMP WITH TIME zone
);
create table if not exists admin_rights(
    id serial primary key,
    name text not null
);
create table if not exists admin_rights_users(
    id serial primary key,
    user_id BIGINT not null REFERENCES telegram_users(id) on DELETE CASCADE,
    right_id BIGINT not null REFERENCES admin_rights(id) on DELETE CASCADE
);
create table if not exists clubs_additional_links(
    id serial primary key,
    club_id BIGINT not null REFERENCES clubs(id) on DELETE CASCADE,
    link text not null,
    button_name text not null,
    created_at timestamp not null default NOW()
);