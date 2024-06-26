-- create table `meads`
create table if not exists meads (
  id integer primary key
  , mead_name string not null
  , start_date datetime not null default (datetime('now','localtime'))
  , yeast_used string not null
  , sugar_source string not null
  , starting_gravity float
  , potential_abv float
  , yield_in_oz float
  , unique(mead_name, start_date)
);
-- create table `mead_notes`
create table if not exists mead_notes (
  id integer primary key
  , mead_id integer not null
  , note string not null
  , note_date datetime not null default (datetime('now','localtime'))
  , foreign key(mead_id) references meads(id)
);
-- create table `activity`
create table if not exists activity (
  id integer primary key
  , mead_id integer not null
  , act_name string not null
  , act_date date not null
  , check (act_name in ('started','racked','bottled','modified','end_at_1','ended_forced','other'))
  , foreign key(mead_id) references meads(id)
);
-- create table `abv_measurements`
create table if not exists abv_measurements (
  id integer primary  key
  , mead_id integer not null
  , sample_date datetime not null default (datetime('now','localtime'))
  , curr_gravity float not null
  , curr_abv float
  , days_since_start int
  , pct_to_pot_abv float
  , foreign key(mead_id) references meads(id)
);
-- create table `ingredient_costs`
create table if not exists ingredient_costs (
  id integer primary  key
  , mead_id integer not null
  , type string not null
  , ingredient string not null
  , cost float not null
  , grams float not null
  , lbs float
  , foreign key(mead_id) references meads(id)
  );