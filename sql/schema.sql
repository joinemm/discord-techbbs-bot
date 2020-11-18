-- db schema goes here
CREATE TABLE IF NOT EXISTS sent_thread (
    thread_id INTEGER,
    PRIMARY KEY (thread_id)
);

CREATE TABLE IF NOT EXISTS search_term (
    term VARCHAR(64),
    guild_id BIGINT,
    channel_id BIGINT,
    PRIMARY KEY (term, channel_id)
);