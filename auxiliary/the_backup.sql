--
-- PostgreSQL database dump
--

-- Dumped from database version 10.16 (Ubuntu 10.16-1.pgdg18.04+1)
-- Dumped by pg_dump version 10.16 (Ubuntu 10.16-1.pgdg18.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: offices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.offices (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    room_nr integer NOT NULL
);


ALTER TABLE public.offices OWNER TO postgres;

--
-- Name: offices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.offices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.offices_id_seq OWNER TO postgres;

--
-- Name: offices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.offices_id_seq OWNED BY public.offices.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    room_id integer NOT NULL,
    room_number integer NOT NULL,
    room_capacity integer NOT NULL,
    transparent boolean NOT NULL,
    available boolean NOT NULL
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- Name: rooms_room_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_room_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rooms_room_id_seq OWNER TO postgres;

--
-- Name: rooms_room_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_room_id_seq OWNED BY public.rooms.room_id;


--
-- Name: offices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offices ALTER COLUMN id SET DEFAULT nextval('public.offices_id_seq'::regclass);


--
-- Name: rooms room_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN room_id SET DEFAULT nextval('public.rooms_room_id_seq'::regclass);


--
-- Data for Name: offices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.offices (id, name, room_nr) FROM stdin;
1	Jaak Vilo	3119
2	Anna Aljanaki	3082
3	Riccardo Tommasini	3106
4	Sulev Reisberg	3108
5	Siyuan Gao	3109
6	Tarun Khajuria	3079
7	Kaido Lepik	3079
8	Mikhail Papkov	3080
9	Modar Sulaiman	3072
10	Taavi Kivisik	3079
11	Joonas Puura	3109
12	Kai Poolakese	2042
13	Alain Jarred Kermis	2042
14	Marianna Laht	2042
15	Lindsay Heather Wojtula	2042
16	Ardi Tampuu	3077
17	Erik Jaaniso	3112
18	Ivan Kuzmin	3096
19	Dage Särg	2042
20	Rait Herman	2042
21	Taavi Luik	2042
22	Varmo Vene	3025
23	Reimo Palm	3012
24	Reelika Suviste	3020
25	Henri Lakk	3012
26	Alo Aasmäe	3023
27	Kaspar Papli	3015
28	Dominique Unruh	3088
29	Boris Kudryashov	3089
30	Yangjia Li	3086
31	Bahman Ghandchi	3071
32	Rafieh Mosaheb	3071
33	Arnis Paršovs	3090
34	Raimundas Matulevicius	3055
35	Mario Ezequiel Scott	3011
36	Orlenys López Pintado	3003
37	Manuel Alejandro Camargo Chavez	3003
38	Rahul Goel	3008
39	Kristiina Rahkema	3006
40	Eero Vainikko	3038
41	Naveed Muhammad	3066
42	Chinmaya Kumar Dehury	3040
43	Kaveh Khoshkhah	3044
44	Mainak Adhikari	3041
45	Mahir Gulzar	3095
46	Mark Fišel	3061
47	Heili Orav	3059
48	Kairit Sirts	3063
49	Andre Tättar	3068
50	Liisa Rätsep	3063
51	Kaili Müürisep	3063
52	Annika Laumets-Tättar	3063
53	Siim Orasmaa	3059
54	Tarmo Vaino	3058
55	Ivar Koppel	3029
56	Terje Vellemaa	3029
57	Hannes Tamme	3032
58	Rasmus Soome	3024
59	Villem Tõnisson	2051
60	Ott Eric Oopkaup	3024
61	Vladislav Tuzov	3032
62	Martin Kaljula	3124
63	Annet Muru	3114
64	Maarja Kungla	3002
65	Anni Suvi	3120
66	Saili Petti	3123
67	Anneli Vainumäe	3123
68	Merlin Pastak	223
69	Reimo Luik	3027
70	Raul Vicente Zafra	3100
71	Kallol Roy	3082
72	Priit Adler	3112
73	Elena Sügis	3109
74	Nurlan Kerimov	3079
75	Samuele Langhi	3105
76	Maarja Pajusalu	3103
77	Ahto Salumets	3079
78	Aqeel Labash	3077
79	Martti Tamm	2042
80	Kersti Jääger	2042
81	Raimond-Hendrik Tunnel	2007
82	Sten-Oliver Salumaa	2042
83	Thamara Luup Carvalho	2042
84	Uku Raudvere	3096
85	Edgar Sepp	3095
86	Ida Maria Orula	2042
87	Helle Hein	3014
88	Ahti Põder	3018
89	Vambola Leping	3016
90	Kalmer Apinis	3022
91	Priit Paluoja	3015
92	Simmo Saan	3023
93	Anti Ingel	3075
94	Raul-Martin Rebane	3086
95	Marlon Gerardo Dumas Menjivar	3004
96	Dietmar Alfred Paul Kurt Pfahl	3007
97	Fredrik Payman Milani	3011
98	Ishaya Peni Gambo	3009
99	Katsiaryna Lashkevich	3010
100	Maria Angelica Medina Angarita	3010
101	Hina Anwar	3006
102	Pelle Jakovits	3040
103	Liyanage Don Mohan Devapriya Liyanage	3044
104	Farooq Ayoub Dar	3044
105	Shivananda Rangappa Poojara	3033
106	Eduard Barbu	3059
107	Kadri Vider	3060
108	Mare Koit	3065
109	Neeme Kahusk	3060
110	Agnes Luhtaru	3033
111	Katrin Tsepelina	3063
112	Ilja Livenson	3028
113	Sander Kuusemets	3032
114	Maxandre Olivier Georges Francois Lucien Ogeret	3095
115	Anders Martoja	3032
116	Sergei Zaiaev	3028
117	Olaf Viikna	3028
118	Iris Merilo	3027
119	Mait Tenslind	3024
120	Jaanika Seli	3122
121	Natali Belinska	3117
122	Henry Narits	3120
123	Reili Liiver	3124
124	Anastasiia Shevchenko	3114
125	Ülar Allas	2051
126	Liivi Luik	3002
127	Maria Laanelepp	3092
128	Daisy Alatare	3117
129	Johann Langemets	4085
130	Krista Fischer	4101
131	Jaan Lellep	4063
132	Arvet Pedas	4098
133	Tõnu Kollo	4073
134	Kati Ain	4060
135	Kaur Lumiste	4079
136	Julia Polikarpus	4060
137	Evely Kirsiaed	4047
138	Mikk Vikerpuur	4099
139	Mohammad Jamsher Ali	4067
140	Svetlana Saprõkova	4104
141	Kelli Sander	4104
142	Kerli Orav-Puurand	4055
143	Viktor Abramov	4102
144	Valdis Laan	4100
145	Jüri Lember	4089
146	Kalle Kaarli	4097
147	Kalev Pärna	4076
148	Kaido Lätt	4092
149	Annely Mürk	4059
150	Indrek Zolk	4072
151	Ago-Erik Riet	4069
152	Enno Kolk	4092
153	Liina Jürimaa	1015
154	Tiina Kraav	4055
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rooms (room_id, room_number, room_capacity, transparent, available) FROM stdin;
2	315	2	t	t
6	319	6	f	t
1	314	5	f	t
3	316	2	f	t
7	400	20	f	t
4	317	5	t	t
5	318	6	t	t
\.


--
-- Name: offices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.offices_id_seq', 154, true);


--
-- Name: rooms_room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_room_id_seq', 7, true);


--
-- Name: offices offices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.offices
    ADD CONSTRAINT offices_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (room_id);


--
-- Name: rooms rooms_room_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_room_number_key UNIQUE (room_number);


--
-- Name: office_user_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX office_user_name_idx ON public.offices USING gin (name public.gin_trgm_ops);


--
-- PostgreSQL database dump complete
--

