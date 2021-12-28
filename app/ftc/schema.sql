DROP TABLE IF EXISTS "events";
CREATE TABLE IF NOT EXISTS "events" (
	"eventID"	INTEGER NOT NULL UNIQUE,
	"MatchID"	INTEGER NOT NULL,
	"Minute"	INTEGER NOT NULL,
	"eventCategoryID"	INTEGER NOT NULL,
	PRIMARY KEY("eventID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "eventCategory";
CREATE TABLE IF NOT EXISTS "eventCategory" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"description"	TEXT NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "goals";
CREATE TABLE IF NOT EXISTS "goals" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"Scorer_ID"	INTEGER NOT NULL,
	"Wingman_ID"	INTEGER,
	"was_Penalty"	INTEGER,
	"was_Owngoal"	INTEGER,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "cards";
CREATE TABLE IF NOT EXISTS "cards" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"ReceivingPlayer"	INTEGER NOT NULL,
	"cardCategory"	INTEGER,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "team_player";
CREATE TABLE IF NOT EXISTS "team_player" (
	"teamID"	INTEGER NOT NULL,
	"playerID"	INTEGER NOT NULL UNIQUE
);
DROP TABLE IF EXISTS "season";
CREATE TABLE IF NOT EXISTS "season" (
	"MatchID"	INTEGER NOT NULL UNIQUE,
	"MatchDay"	INTEGER,
	"IsFirstLeg"	INTEGER,
	"Season"	INTEGER NOT NULL,
	"HomeTeamID"	INTEGER NOT NULL,
	"AwayTeamID"	INTEGER NOT NULL,
	"HomeGoals"	INTEGER,
	"AwayGoals"	INTEGER,
	"Result"	INTEGER,
	"Is_Finished"	INTEGER DEFAULT 0,
	PRIMARY KEY("MatchID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "gamer";
CREATE TABLE IF NOT EXISTS "gamer" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"UserID" INTEGER DEFAULT 0,
	"FirstName"	TEXT NOT NULL,
	"LastName"	TEXT NOT NULL,
	"TeamName"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "user";
CREATE TABLE IF NOT EXISTS "user" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"UserName"	TEXT NOT NULL UNIQUE,
	"Password"	TEXT NOT NULL,
	"IsAdmin"	INTEGER DEFAULT 0,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

DROP TABLE IF EXISTS "players";
CREATE TABLE IF NOT EXISTS "players" (
	"ID"	INTEGER UNIQUE,
	"player_url"	TEXT,
	"short_name"	TEXT,
	"long_name"	TEXT,
	"player_positions"	TEXT,
	"overall"	INTEGER,
	"potential"	INTEGER,
	"value_eur"	INTEGER,
	"wage_eur"	INTEGER,
	"age"	INTEGER,
	"dob"	TEXT,
	"height_cm"	INTEGER,
	"weight_kg"	INTEGER,
	"club_name"	TEXT,
	"league_name"	TEXT,
	"league_level"	REAL,
	"club_position"	TEXT,
	"club_jersey_number"	REAL,
	"club_loaned_from"	TEXT,
	"club_joined"	TEXT,
	"club_contract_valid_until"	REAL,
	"nationality"	TEXT,
	"nation_position"	TEXT,
	"nation_jersey_number"	REAL,
	"preferred_foot"	TEXT,
	"weak_foot"	INTEGER,
	"skill_moves"	INTEGER,
	"international_reputation"	INTEGER,
	"work_rate"	TEXT,
	"body_type"	TEXT,
	"real_face"	TEXT,
	"release_clause_eur"	REAL,
	"player_tags"	TEXT,
	"player_traits"	TEXT,
	"pace"	REAL,
	"shooting"	REAL,
	"passing"	REAL,
	"dribbling"	REAL,
	"defending"	REAL,
	"physic"	REAL,
	"attacking_crossing"	INTEGER,
	"attacking_finishing"	INTEGER,
	"attacking_heading_accuracy"	INTEGER,
	"attacking_short_passing"	INTEGER,
	"attacking_volleys"	INTEGER,
	"skill_dribbling"	INTEGER,
	"skill_curve"	INTEGER,
	"skill_fk_accuracy"	INTEGER,
	"skill_long_passing"	INTEGER,
	"skill_ball_control"	INTEGER,
	"movement_acceleration"	INTEGER,
	"movement_sprint_speed"	INTEGER,
	"movement_agility"	INTEGER,
	"movement_reactions"	INTEGER,
	"movement_balance"	INTEGER,
	"power_shot_power"	INTEGER,
	"power_jumping"	INTEGER,
	"power_stamina"	INTEGER,
	"power_strength"	INTEGER,
	"power_long_shots"	INTEGER,
	"mentality_aggression"	INTEGER,
	"mentality_interceptions"	INTEGER,
	"mentality_positioning"	INTEGER,
	"mentality_vision"	INTEGER,
	"mentality_penalties"	INTEGER,
	"mentality_composure"	INTEGER,
	"defending_marking_awareness"	INTEGER,
	"defending_standing_tackle"	INTEGER,
	"defending_sliding_tackle"	INTEGER,
	"goalkeeping_diving"	INTEGER,
	"goalkeeping_handling"	INTEGER,
	"goalkeeping_kicking"	INTEGER,
	"goalkeeping_positioning"	INTEGER,
	"goalkeeping_reflexes"	INTEGER,
	"goalkeeping_speed"	REAL,
	"ls"	TEXT,
	"st"	TEXT,
	"rs"	TEXT,
	"lw"	TEXT,
	"lf"	TEXT,
	"cf"	TEXT,
	"rf"	TEXT,
	"rw"	TEXT,
	"lam"	TEXT,
	"cam"	TEXT,
	"ram"	TEXT,
	"lm"	TEXT,
	"lcm"	TEXT,
	"cm"	TEXT,
	"rcm"	TEXT,
	"rm"	TEXT,
	"lwb"	TEXT,
	"ldm"	TEXT,
	"cdm"	TEXT,
	"rdm"	TEXT,
	"rwb"	TEXT,
	"lb"	TEXT,
	"lcb"	TEXT,
	"cb"	TEXT,
	"rcb"	TEXT,
	"rb"	TEXT,
	"gk"	TEXT,
	"player_face_url"	TEXT,
	"club_logo_url"	TEXT,
	"club_flag_url"	TEXT,
	"nation_logo_url"	TEXT,
	"nation_flag_url"	TEXT
);
INSERT INTO "eventCategory" VALUES (1,'Tor');
INSERT INTO "eventCategory" VALUES (2,'Karte');