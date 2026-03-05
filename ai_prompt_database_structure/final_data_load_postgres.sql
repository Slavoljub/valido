-- ============================================================================
-- FINAL DATA LOAD TO REACH 50+ RECORDS PER TABLE
-- Using postgres:postgres credentials
-- ============================================================================

-- Connect to database with postgres:postgres
\c ai_valido_online postgres;

-- ============================================================================
-- ADD MORE COMPANIES TO REACH 50+ TOTAL
-- ============================================================================

INSERT INTO companies (
    company_name, legal_name, tax_id, registration_number,
    business_entity_type_id, business_area_id, country_id,
    address_line1, city, phone, email, description, is_active
) VALUES
-- Continue adding Serbian companies with Cyrillic
('Суботица Медиа ДОО', 'Суботица Медиа ДОО', '111111113', 'BD11111113',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Улица Корзо 15', 'Суботица', '+38124567891', 'info@submed.rs',
 'Медијска компанија из Суботице специјализована за локалне вести и садржај', true),

('Врање Текстил ДОО', 'Врање Текстил ДОО', '222222224', 'BD22222224',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'MANUFACT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Индустријска зона 12', 'Врање', '+38117345679', 'info@vrntextil.rs',
 'Текстилна индустрија из Врања са традиционалном производњом', true),

('Краљево Метал ДОО', 'Краљево Метал ДОО', '333333335', 'BD33333335',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'MANUFACT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Улица Вука Караџића 25', 'Краљево', '+38136234568', 'info@krgmetal.rs',
 'Метална индустрија из Краљева специјализована за металну конструкцију', true),

('Сремска Митровица Логистика ДОО', 'Сремска Митровица Логистика ДОО', '444444446', 'BD44444446',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'TRANSP'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Речни терминал 8', 'Сремска Митровица', '+38122678902', 'info@smmlog.rs',
 'Логистичка компанија из Сремске Митровице са речним транспортним услугама', true),

('Лозница Производња ДОО', 'Лозница Производња ДОО', '555555557', 'BD55555557',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'MANUFACT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Индустријски парк 18', 'Лозница', '+38115234568', 'info@lozprod.rs',
 'Производна компанија из Лознице специјализована за дрвену грађу', true),

('Уб Здравство ДОО', 'Уб Здравство ДОО', '666666668', 'BD66666668',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Булевар Ослобођења 33', 'Уб', '+38115345679', 'info@ubhealth.rs',
 'Здравствене услуге из Уба са модерном опремом', true),

('Алексинац Пољопривреда ДОО', 'Алексинац Пољопривреда ДОО', '777777779', 'BD77777779',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'AGRIC'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Село Прћиловица', 'Алексинац', '+38118345678', 'info@aleksagri.rs',
 'Пољопривредна компанија из Алексинца специјализована за воће и поврће', true),

('Крушевац Туризам ДОО', 'Крушевац Туризам ДОО', '888888890', 'BD88888890',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Трг Срба 8', 'Крушевац', '+38137234568', 'info@krustur.rs',
 'Туристичка агенција из Крушевца са фокусом на културни туризам', true),

('Ваљево Електроника ДОО', 'Ваљево Електроника ДОО', '999999991', 'BD99999991',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'IT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Технички факултет 22', 'Ваљево', '+38114567891', 'info@valjevoelec.rs',
 'Електронска компанија из Ваљева са IoT решењима за пољопривреду', true),

('Ниш Фармацеутика ДОО', 'Ниш Фармацеутика ДОО', '101010103', 'BD10101013',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'RS'),
 'Булевар Медицински 45', 'Ниш', '+38118456790', 'info@nispharma.rs',
 'Фармацеутска компанија из Ниша са производњом природних лекова', true),

-- Add international companies to reach 50+ total
('Tech Solutions GmbH', 'Tech Solutions GmbH', '1234567890123', 'DE123456789',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'IT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'DE'),
 'Hauptstraße 123', 'Berlin', '+493012345678', 'info@techsolutions.de',
 'German software development company specializing in enterprise solutions', true),

('Innovation Labs Inc', 'Innovation Labs Inc', '9876543210987', 'US987654321',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'IT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'US'),
 'Silicon Valley 456', 'California', '+16501234567', 'info@innovationlabs.com',
 'American innovation lab focusing on AI and machine learning research', true),

('Global Consulting Ltd', 'Global Consulting Ltd', '4567891234567', 'GB456789123',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'GB'),
 'London Street 789', 'London', '+441234567890', 'info@globalconsulting.co.uk',
 'British consulting firm specializing in digital transformation', true),

('Manufacturing Excellence SA', 'Manufacturing Excellence SA', '7891234567891', 'FR789123456',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'MANUFACT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'FR'),
 'Rue de l''Industrie 321', 'Paris', '+33123456789', 'info@manufacturing.fr',
 'French manufacturing company with excellence in automotive parts', true),

('EcoEnergy Solutions BV', 'EcoEnergy Solutions BV', '3216549873216', 'NL321654987',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'ENERGY'),
 (SELECT countries_id FROM countries WHERE iso_code = 'NL'),
 'Energieplein 654', 'Amsterdam', '+31201234567', 'info@ecoenergy.nl',
 'Dutch renewable energy company specializing in solar and wind solutions', true),

('Digital Marketing Pro SRL', 'Digital Marketing Pro SRL', '6549873216549', 'IT654987321',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'IT'),
 'Via Digitale 987', 'Milan', '+39021234567', 'info@digitalmarketing.it',
 'Italian digital marketing agency with international clients', true),

('Food Processing Corp', 'Food Processing Corp', '9873216549873', 'ES987321654',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'AGRIC'),
 (SELECT countries_id FROM countries WHERE iso_code = 'ES'),
 'Calle Alimentaria 147', 'Barcelona', '+34987654321', 'info@foodprocessing.es',
 'Spanish food processing company specializing in Mediterranean products', true),

('Transport Logistics GmbH', 'Transport Logistics GmbH', '1472583691472', 'AT147258369',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'TRANSP'),
 (SELECT countries_id FROM countries WHERE iso_code = 'AT'),
 'Transportweg 258', 'Vienna', '+43123456789', 'info@transportlogistics.at',
 'Austrian logistics company with European transport network', true),

('Healthcare Systems AS', 'Healthcare Systems AS', '3691472583691', 'SE369147258',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'SE'),
 'Sjukvårdsgatan 369', 'Stockholm', '+46701234567', 'info@healthcaresystems.se',
 'Swedish healthcare systems provider with innovative medical solutions', true),

('Agriculture Tech Ltd', 'Agriculture Tech Ltd', '7418529637418', 'AU741852963',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'AGRIC'),
 (SELECT countries_id FROM countries WHERE iso_code = 'AU'),
 'AgriTech Road 852', 'Sydney', '+61123456789', 'info@agritech.au',
 'Australian agriculture technology company developing smart farming solutions', true),

('Construction Masters Oy', 'Construction Masters Oy', '8529637418529', 'FI852963741',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'CONSTR'),
 (SELECT countries_id FROM countries WHERE iso_code = 'FI'),
 'Rakentajantie 963', 'Helsinki', '+358123456789', 'info@construction.fi',
 'Finnish construction company with expertise in sustainable building', true),

('Retail Solutions PLC', 'Retail Solutions PLC', '9637418529637', 'IE963741852',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'TRADE'),
 (SELECT countries_id FROM countries WHERE iso_code = 'IE'),
 'Retail Street 741', 'Dublin', '+353123456789', 'info@retailsolutions.ie',
 'Irish retail solutions company specializing in e-commerce platforms', true),

('Chemical Industries SA', 'Chemical Industries SA', '1597534681597', 'PT159753468',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'MANUFACT'),
 (SELECT countries_id FROM countries WHERE iso_code = 'PT'),
 'Rua Industrial 357', 'Lisbon', '+351234567890', 'info@chemical.pt',
 'Portuguese chemical industry company with sustainable production methods', true),

('Media Production BV', 'Media Production BV', '3571597533571', 'BE357159753',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'SERVICES'),
 (SELECT countries_id FROM countries WHERE iso_code = 'BE'),
 'Mediaweg 159', 'Brussels', '+32234567890', 'info@mediaproduction.be',
 'Belgian media production company creating content for European markets', true),

('Energy Services Ltd', 'Energy Services Ltd', '7531593577531', 'DK753159357',
 (SELECT business_entity_types_id FROM business_entity_types WHERE entity_code = 'DOO'),
 (SELECT business_areas_id FROM business_areas WHERE area_code = 'ENERGY'),
 (SELECT countries_id FROM countries WHERE iso_code = 'DK'),
 'Energivej 357', 'Copenhagen', '+453456789012', 'info@energyservices.dk',
 'Danish energy services company focusing on green energy transition', true)

ON CONFLICT (tax_id) DO NOTHING;

-- ============================================================================
-- ADD MORE USERS TO REACH 50+ TOTAL
-- ============================================================================

INSERT INTO users (
    companies_id, username, email, first_name, last_name,
    phone, user_role, is_active
) VALUES
-- More Serbian users
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'petar_p', 'petar@codevalido.rs',
 'Петар', 'Петровић', '+381641010102', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'sara_m', 'sara@codevalido.rs',
 'Сара', 'Марковић', '+381641111113', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'luka_s', 'luka@codevalido.rs',
 'Лука', 'Стефановић', '+381641222224', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'sofija_t', 'sofija@codevalido.rs',
 'Софија', 'Тодоровић', '+381641333335', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'dusan_k', 'dusan@codevalido.rs',
 'Душан', 'Ковачевић', '+381641444446', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'mina_r', 'mina@codevalido.rs',
 'Мина', 'Радић', '+381641555557', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'filip_b', 'filip@codevalido.rs',
 'Филип', 'Благојевић', '+381641666668', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'tara_g', 'tara@codevalido.rs',
 'Тара', 'Грбић', '+381641777779', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'vuk_m', 'vuk@codevalido.rs',
 'Вук', 'Миленковић', '+381641888880', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'leonora_p', 'leonora@codevalido.rs',
 'Леонoра', 'Павловић', '+381641999991', 'user', true),

-- More international users
((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'john_d', 'john@codevalido.rs',
 'John', 'Doe', '+12345678901', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'jane_s', 'jane@codevalido.rs',
 'Jane', 'Smith', '+12345678902', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'mike_j', 'mike@codevalido.rs',
 'Mike', 'Johnson', '+12345678903', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'sarah_w', 'sarah@codevalido.rs',
 'Sarah', 'Williams', '+12345678904', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'david_b', 'david@codevalido.rs',
 'David', 'Brown', '+12345678905', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'emma_d', 'emma@codevalido.rs',
 'Emma', 'Davis', '+12345678906', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'chris_m', 'chris@codevalido.rs',
 'Chris', 'Miller', '+12345678907', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'lisa_w', 'lisa@codevalido.rs',
 'Lisa', 'Wilson', '+12345678908', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'alex_t', 'alex@codevalido.rs',
 'Alex', 'Taylor', '+12345678909', 'user', true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'), 'rachel_h', 'rachel@codevalido.rs',
 'Rachel', 'Harris', '+12345678910', 'user', true),

-- Additional users for other companies
((SELECT companies_id FROM companies WHERE tax_id = '111111113'), 'admin_sub', 'admin@submed.rs',
 'Администратор', 'Суботица', '+38124567891', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '222222224'), 'admin_vrn', 'admin@vrntextil.rs',
 'Администратор', 'Врање', '+38117345679', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '333333335'), 'admin_krg', 'admin@krgmetal.rs',
 'Администратор', 'Краљево', '+38136234568', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '444444446'), 'admin_smm', 'admin@smmlog.rs',
 'Администратор', 'Сремска Митровица', '+38122678902', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '555555557'), 'admin_loz', 'admin@lozprod.rs',
 'Администратор', 'Лозница', '+38115234568', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '666666668'), 'admin_ub', 'admin@ubhealth.rs',
 'Администратор', 'Уб', '+38115345679', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '777777779'), 'admin_aleks', 'admin@aleksagri.rs',
 'Администратор', 'Алексинац', '+38118345678', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '888888890'), 'admin_krus', 'admin@krustur.rs',
 'Администратор', 'Крушевац', '+38137234568', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '999999991'), 'admin_valj', 'admin@valjevoelec.rs',
 'Администратор', 'Ваљево', '+38114567891', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '101010103'), 'admin_nis', 'admin@nispharma.rs',
 'Администратор', 'Ниш', '+38118456790', 'admin', true),

-- International company users
((SELECT companies_id FROM companies WHERE tax_id = '1234567890123'), 'admin_de', 'admin@techsolutions.de',
 'Administrator', 'Deutschland', '+493012345678', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '9876543210987'), 'admin_us', 'admin@innovationlabs.com',
 'Administrator', 'USA', '+16501234567', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '4567891234567'), 'admin_gb', 'admin@globalconsulting.co.uk',
 'Administrator', 'UK', '+441234567890', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '7891234567891'), 'admin_fr', 'admin@manufacturing.fr',
 'Administrator', 'France', '+33123456789', 'admin', true),

((SELECT companies_id FROM companies WHERE tax_id = '3216549873216'), 'admin_nl', 'admin@ecoenergy.nl',
 'Administrator', 'Netherlands', '+31201234567', 'admin', true)

ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- ADD CUSTOMER FEEDBACK TO REACH 50+ TOTAL
-- ============================================================================

INSERT INTO customer_feedback (
    companies_id, users_id, feedback_type, feedback_source,
    title, content, content_language, sentiment_score, sentiment_label,
    rating_given, nps_score, ai_processed
) VALUES
-- More Serbian feedback to reach 50+ total
((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'milana@codevalido.rs'),
 'review', 'website',
 'Одлична подршка корисницима', 'Подршка корисницима је изузетна. Сви проблеми су решени у року од 24 сата.',
 'sr-RS', 0.93, 'positive', 5, 10, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'nikola@codevalido.rs'),
 'review', 'email',
 'Професионалан тим', 'Тим је веома професионалан и експертан. Све захтеве смо добили на време.',
 'sr-RS', 0.89, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'ana@codevalido.rs'),
 'suggestion', 'survey',
 'Побољшање корисничког искуства', 'Можда би било добро додати мобилну апликацију за брже пријављивање проблема.',
 'sr-RS', 0.55, 'neutral', 4, 7, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'marko@codevalido.rs'),
 'review', 'website',
 'Висок квалитет услуга', 'Квалитет услуга је на високом нивоу. Све препоруке су професионално реализоване.',
 'sr-RS', 0.91, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'jelena@codevalido.rs'),
 'review', 'social',
 'Задовољство сарадњом', 'Врло смо задовољни сарадњом са компанијом. Све је било по договору.',
 'sr-RS', 0.87, 'positive', 5, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'vladimir@codevalido.rs'),
 'praise', 'website',
 'Фантастични резултати', 'Резултати премашују наша очекивања. Фантастична сарадња!',
 'sr-RS', 0.96, 'positive', 5, 10, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'marija@codevalido.rs'),
 'review', 'email',
 'Добра комуникација', 'Комуникација са тимом је била одлична. Сви рокови су поштовани.',
 'sr-RS', 0.88, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'stefan@codevalido.rs'),
 'suggestion', 'survey',
 'Више интеграција', 'Било би одлично имати интеграцију са још неким популарним алатима.',
 'sr-RS', 0.48, 'neutral', 4, 6, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'ivana@codevalido.rs'),
 'review', 'website',
 'Препоручујемо', 'Апсолутно препоручујемо ову компанију. Квалитет на највишем нивоу.',
 'sr-RS', 0.94, 'positive', 5, 10, true),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'aleksandar@codevalido.rs'),
 'review', 'social',
 'Врло професионално', 'Веома професионалан приступ послу. Све је испоручено квалитетно.',
 'sr-RS', 0.90, 'positive', 5, 9, true),

-- More feedback for different companies
((SELECT companies_id FROM companies WHERE tax_id = '111111113'),
 NULL, 'review', 'website',
 'Одличне медијске услуге', 'Веома смо задовољни медијским услугама. Професионалан приступ.',
 'sr-RS', 0.92, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '222222224'),
 NULL, 'review', 'email',
 'Квалитетна текстилна производња', 'Текстилни производи су високог квалитета. Добра цена.',
 'sr-RS', 0.85, 'positive', 4, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '333333335'),
 NULL, 'review', 'website',
 'Металне конструкције', 'Металне конструкције су стабилне и добро израђене. Препоручујемо.',
 'sr-RS', 0.88, 'positive', 5, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '444444446'),
 NULL, 'review', 'survey',
 'Ефикасна логистика', 'Логистички сервис је веома ефикасан. Брза достава и добра организација.',
 'sr-RS', 0.90, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '555555557'),
 NULL, 'review', 'website',
 'Квалитетна дрвена грађа', 'Дрвена грађа је високог квалитета. Одлична обрада и финиш.',
 'sr-RS', 0.87, 'positive', 4, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '666666668'),
 NULL, 'review', 'email',
 'Здравствене услуге', 'Здравствене услуге су на високом нивоу. Пријатно особље и добра опрема.',
 'sr-RS', 0.91, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '777777779'),
 NULL, 'review', 'website',
 'Пољопривредни производи', 'Пољопривредни производи су свеже и квалитетне. Добра сарадња.',
 'sr-RS', 0.89, 'positive', 5, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '888888890'),
 NULL, 'review', 'social',
 'Туристичке услуге', 'Туристичке услуге су одличне. Добар избор дестинација и организација.',
 'sr-RS', 0.93, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '999999991'),
 NULL, 'review', 'website',
 'Електронски производи', 'Електронски производи су квалитетни. Добра техничка подршка.',
 'sr-RS', 0.86, 'positive', 4, 8, true),

((SELECT companies_id FROM companies WHERE tax_id = '101010103'),
 NULL, 'review', 'email',
 'Фармацеутски производи', 'Фармацеутски производи су ефикасни. Природни састојци и добра цена.',
 'sr-RS', 0.88, 'positive', 5, 8, true),

-- International feedback
((SELECT companies_id FROM companies WHERE tax_id = '1234567890123'),
 NULL, 'review', 'website',
 'Excellent German software', 'The software solutions are excellent. Professional team and great quality.',
 'de-DE', 0.94, 'positive', 5, 10, true),

((SELECT companies_id FROM companies WHERE tax_id = '9876543210987'),
 NULL, 'review', 'email',
 'Innovative American company', 'Very innovative company with cutting-edge AI solutions. Highly recommended.',
 'en-US', 0.96, 'positive', 5, 10, true),

((SELECT companies_id FROM companies WHERE tax_id = '4567891234567'),
 NULL, 'review', 'website',
 'Professional British consulting', 'Professional consulting services with excellent results. Very satisfied.',
 'en-GB', 0.92, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '7891234567891'),
 NULL, 'review', 'email',
 'Qualité française', 'Les produits sont de très haute qualité. Service excellent et livraison rapide.',
 'fr-FR', 0.90, 'positive', 5, 9, true),

((SELECT companies_id FROM companies WHERE tax_id = '3216549873216'),
 NULL, 'review', 'website',
 'Duurzame energie', 'Uitstekende duurzame energie oplossingen. Goede technische ondersteuning.',
 'nl-NL', 0.88, 'positive', 4, 8, true)

ON CONFLICT (content_hash) DO NOTHING;

-- ============================================================================
-- FINAL VERIFICATION
-- ============================================================================

DO $$
DECLARE
    comp_count INTEGER;
    user_count INTEGER;
    feedback_count INTEGER;
    ai_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO comp_count FROM companies;
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO feedback_count FROM customer_feedback;
    SELECT COUNT(*) INTO ai_count FROM ai_models;

    RAISE NOTICE 'FINAL DATA LOAD VERIFICATION:';
    RAISE NOTICE 'Companies: %', comp_count;
    RAISE NOTICE 'Users: %', user_count;
    RAISE NOTICE 'Customer Feedback: %', feedback_count;
    RAISE NOTICE 'AI Models: %', ai_count;

    IF comp_count >= 50 THEN
        RAISE NOTICE '✅ COMPANIES: TARGET ACHIEVED (50+ records: %)', comp_count;
    ELSE
        RAISE NOTICE '❌ COMPANIES: TARGET NOT ACHIEVED (Current: %, Need: 50+)', comp_count;
    END IF;

    IF user_count >= 50 THEN
        RAISE NOTICE '✅ USERS: TARGET ACHIEVED (50+ records: %)', user_count;
    ELSE
        RAISE NOTICE '❌ USERS: TARGET NOT ACHIEVED (Current: %, Need: 50+)', user_count;
    END IF;

    IF feedback_count >= 50 THEN
        RAISE NOTICE '✅ CUSTOMER FEEDBACK: TARGET ACHIEVED (50+ records: %)', feedback_count;
    ELSE
        RAISE NOTICE '❌ CUSTOMER FEEDBACK: TARGET NOT ACHIEVED (Current: %, Need: 50+)', feedback_count;
    END IF;

    RAISE NOTICE 'Data loading completed using postgres:postgres credentials!';
END $$;
