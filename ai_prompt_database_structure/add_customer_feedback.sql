-- ============================================================================
-- ADD CUSTOMER FEEDBACK RECORDS
-- Using postgres:postgres credentials
-- ============================================================================

-- Connect to database with postgres:postgres
\c ai_valido_online postgres;

-- ============================================================================
-- ADD CUSTOMER FEEDBACK RECORDS TO REACH 50+ TOTAL
-- ============================================================================

-- Add feedback records with proper content_hash generation
INSERT INTO customer_feedback (
    companies_id, users_id, feedback_type, feedback_source,
    title, content, content_language, sentiment_score, sentiment_label,
    rating_given, nps_score, ai_processed, content_hash
) VALUES
-- Serbian feedback
((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'milana@codevalido.rs'),
 'review', 'website',
 'Веома добар софтвер', 'Веома смо задовољни квалитетом софтвера и професионалном подршком тима.',
 'sr-RS', 0.92, 'positive', 5, 9, true, md5('Веома смо задовољни квалитетом софтвера и професионалном подршком тима.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'nikola@codevalido.rs'),
 'review', 'email',
 'Одлична сарадња', 'Сарадња са компанијом је била одлична. Професионалан приступ.',
 'sr-RS', 0.88, 'positive', 5, 10, true, md5('Сарадња са компанијом је била одлична. Професионалан приступ.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'ana@codevalido.rs'),
 'suggestion', 'survey',
 'Предлог за унапређење', 'Можда би било добро додати мобилну апликацију.',
 'sr-RS', 0.45, 'neutral', 4, 7, true, md5('Можда би било добро додати мобилну апликацију.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'marko@codevalido.rs'),
 'review', 'website',
 'Висок квалитет', 'Квалитет услуга је на високом нивоу.',
 'sr-RS', 0.91, 'positive', 5, 9, true, md5('Квалитет услуга је на високом нивоу.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 (SELECT users_id FROM users WHERE email = 'jelena@codevalido.rs'),
 'review', 'social',
 'Задовољство сарадњом', 'Врло смо задовољни сарадњом са компанијом.',
 'sr-RS', 0.87, 'positive', 5, 8, true, md5('Врло смо задовољни сарадњом са компанијом.')),

-- More feedback for different companies
((SELECT companies_id FROM companies WHERE tax_id = '111111113'),
 NULL, 'review', 'website',
 'Одличне медијске услуге', 'Веома смо задовољни медијским услугама.',
 'sr-RS', 0.92, 'positive', 5, 9, true, md5('Веома смо задовољни медијским услугама.')),

((SELECT companies_id FROM companies WHERE tax_id = '222222224'),
 NULL, 'review', 'email',
 'Квалитетна производња', 'Производи су високог квалитета.',
 'sr-RS', 0.85, 'positive', 4, 8, true, md5('Производи су високог квалитета.')),

((SELECT companies_id FROM companies WHERE tax_id = '333333335'),
 NULL, 'review', 'website',
 'Металне конструкције', 'Конструкције су стабилне и добро израђене.',
 'sr-RS', 0.88, 'positive', 5, 8, true, md5('Конструкције су стабилне и добро израђене.')),

((SELECT companies_id FROM companies WHERE tax_id = '444444446'),
 NULL, 'review', 'survey',
 'Ефикасна логистика', 'Логистички сервис је веома ефикасан.',
 'sr-RS', 0.90, 'positive', 5, 9, true, md5('Логистички сервис је веома ефикасан.')),

((SELECT companies_id FROM companies WHERE tax_id = '555555557'),
 NULL, 'review', 'website',
 'Квалитетна грађа', 'Дрвена грађа је високог квалитета.',
 'sr-RS', 0.87, 'positive', 4, 8, true, md5('Дрвена грађа је високог квалитета.')),

-- International feedback
((SELECT companies_id FROM companies WHERE tax_id = '1234567890123'),
 NULL, 'review', 'website',
 'Excellent software', 'The software solutions are excellent.',
 'en-US', 0.94, 'positive', 5, 10, true, md5('The software solutions are excellent.')),

((SELECT companies_id FROM companies WHERE tax_id = '9876543210987'),
 NULL, 'review', 'email',
 'Innovative company', 'Very innovative company with great solutions.',
 'en-US', 0.96, 'positive', 5, 10, true, md5('Very innovative company with great solutions.')),

((SELECT companies_id FROM companies WHERE tax_id = '4567891234567'),
 NULL, 'review', 'website',
 'Professional service', 'Professional consulting services.',
 'en-GB', 0.92, 'positive', 5, 9, true, md5('Professional consulting services.')),

((SELECT companies_id FROM companies WHERE tax_id = '7891234567891'),
 NULL, 'review', 'email',
 'Quality manufacturing', 'High quality manufacturing standards.',
 'en-US', 0.90, 'positive', 5, 9, true, md5('High quality manufacturing standards.')),

((SELECT companies_id FROM companies WHERE tax_id = '3216549873216'),
 NULL, 'review', 'website',
 'Green energy solutions', 'Excellent renewable energy solutions.',
 'en-US', 0.88, 'positive', 4, 8, true, md5('Excellent renewable energy solutions.')),

-- Additional feedback to reach 50+
((SELECT companies_id FROM companies WHERE tax_id = '666666668'),
 NULL, 'review', 'email',
 'Здравствене услуге', 'Здравствене услуге су на високом нивоу.',
 'sr-RS', 0.91, 'positive', 5, 9, true, md5('Здравствене услуге су на високом нивоу.')),

((SELECT companies_id FROM companies WHERE tax_id = '777777779'),
 NULL, 'review', 'website',
 'Пољопривредни производи', 'Пољопривредни производи су квалитетни.',
 'sr-RS', 0.89, 'positive', 5, 8, true, md5('Пољопривредни производи су квалитетни.')),

((SELECT companies_id FROM companies WHERE tax_id = '888888890'),
 NULL, 'review', 'social',
 'Туристичке услуге', 'Туристичке услуге су одличне.',
 'sr-RS', 0.93, 'positive', 5, 9, true, md5('Туристичке услуге су одличне.')),

((SELECT companies_id FROM companies WHERE tax_id = '999999991'),
 NULL, 'review', 'website',
 'Електронски производи', 'Електронски производи су квалитетни.',
 'sr-RS', 0.86, 'positive', 4, 8, true, md5('Електронски производи су квалитетни.')),

((SELECT companies_id FROM companies WHERE tax_id = '101010103'),
 NULL, 'review', 'email',
 'Фармацеутски производи', 'Фармацеутски производи су ефикасни.',
 'sr-RS', 0.88, 'positive', 5, 8, true, md5('Фармацеутски производи су ефикасни.')),

-- More international feedback
((SELECT companies_id FROM companies WHERE tax_id = '6549873216549'),
 NULL, 'review', 'website',
 'Digital marketing', 'Excellent digital marketing services.',
 'en-US', 0.85, 'positive', 4, 8, true, md5('Excellent digital marketing services.')),

((SELECT companies_id FROM companies WHERE tax_id = '9873216549873'),
 NULL, 'review', 'email',
 'Food processing', 'High quality food processing standards.',
 'en-US', 0.87, 'positive', 4, 8, true, md5('High quality food processing standards.')),

((SELECT companies_id FROM companies WHERE tax_id = '1472583691472'),
 NULL, 'review', 'website',
 'Transport logistics', 'Efficient transport and logistics services.',
 'en-US', 0.90, 'positive', 5, 9, true, md5('Efficient transport and logistics services.')),

((SELECT companies_id FROM companies WHERE tax_id = '3691472583691'),
 NULL, 'review', 'email',
 'Healthcare systems', 'Innovative healthcare systems and solutions.',
 'en-US', 0.92, 'positive', 5, 9, true, md5('Innovative healthcare systems and solutions.')),

((SELECT companies_id FROM companies WHERE tax_id = '7418529637418'),
 NULL, 'review', 'website',
 'Agriculture technology', 'Advanced agriculture technology solutions.',
 'en-US', 0.89, 'positive', 5, 8, true, md5('Advanced agriculture technology solutions.')),

-- Continue adding more feedback records...
((SELECT companies_id FROM companies WHERE tax_id = '8529637418529'),
 NULL, 'review', 'website',
 'Sustainable construction', 'Excellent sustainable building practices.',
 'en-US', 0.91, 'positive', 5, 9, true, md5('Excellent sustainable building practices.')),

((SELECT companies_id FROM companies WHERE tax_id = '9637418529637'),
 NULL, 'review', 'email',
 'E-commerce solutions', 'Great e-commerce platform solutions.',
 'en-US', 0.88, 'positive', 4, 8, true, md5('Great e-commerce platform solutions.')),

((SELECT companies_id FROM companies WHERE tax_id = '1597534681597'),
 NULL, 'review', 'website',
 'Chemical industry', 'Sustainable chemical production methods.',
 'en-US', 0.85, 'positive', 4, 8, true, md5('Sustainable chemical production methods.')),

((SELECT companies_id FROM companies WHERE tax_id = '3571597533571'),
 NULL, 'review', 'email',
 'Media production', 'High quality media content production.',
 'en-US', 0.87, 'positive', 4, 8, true, md5('High quality media content production.')),

((SELECT companies_id FROM companies WHERE tax_id = '7531593577531'),
 NULL, 'review', 'website',
 'Green energy transition', 'Leading green energy solutions.',
 'en-US', 0.93, 'positive', 5, 9, true, md5('Leading green energy solutions.')),

-- More Serbian feedback to reach target
((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Професионална подршка', 'Подршка корисницима је изузетна.',
 'sr-RS', 0.90, 'positive', 5, 9, true, md5('Подршка корисницима је изузетна.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Квалитетан софтвер', 'Софтвер је високог квалитета.',
 'sr-RS', 0.87, 'positive', 4, 8, true, md5('Софтвер је високог квалитета.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'suggestion', 'survey',
 'Нови функционалности', 'Било би добро додати нове функционалности.',
 'sr-RS', 0.50, 'neutral', 4, 7, true, md5('Било би добро додати нове функционалности.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'social',
 'Одлична сарадња', 'Сарадња је била одлична.',
 'sr-RS', 0.92, 'positive', 5, 10, true, md5('Сарадња је била одлична.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Препоручујемо', 'Апсолутно препоручујемо ову компанију.',
 'sr-RS', 0.94, 'positive', 5, 10, true, md5('Апсолутно препоручујемо ову компанију.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Висока професионалност', 'Тим показује високу професионалност.',
 'sr-RS', 0.89, 'positive', 5, 9, true, md5('Тим показује високу професионалност.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'suggestion', 'survey',
 'Побољшање интерфејса', 'Интерфејс би могао да буде још интуитивнији.',
 'sr-RS', 0.60, 'neutral', 4, 7, true, md5('Интерфејс би могао да буде још интуитивнији.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Брза испорука', 'Пројекат је испоручен на време.',
 'sr-RS', 0.85, 'positive', 4, 8, true, md5('Пројекат је испоручен на време.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'social',
 'Добра цена', 'Однос квалитета и цене је одличан.',
 'sr-RS', 0.82, 'positive', 4, 8, true, md5('Однос квалитета и цене је одличан.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Инновације', 'Компанија уводи корисне иновације.',
 'sr-RS', 0.88, 'positive', 5, 8, true, md5('Компанија уводи корисне иновације.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Техничка подршка', 'Техничка подршка је веома добра.',
 'sr-RS', 0.91, 'positive', 5, 9, true, md5('Техничка подршка је веома добра.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'suggestion', 'survey',
 'Више обука', 'Било би добро имати више обука за кориснике.',
 'sr-RS', 0.55, 'neutral', 4, 7, true, md5('Било би добро имати више обука за кориснике.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Модерна технологија', 'Користи се модерна и напредна технологија.',
 'sr-RS', 0.93, 'positive', 5, 9, true, md5('Користи се модерна и напредна технологија.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'social',
 'Флексибилност', 'Компанија је веома флексибилна.',
 'sr-RS', 0.86, 'positive', 4, 8, true, md5('Компанија је веома флексибилна.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Дугорочна сарадња', 'Спремни смо за дугорочну сарадњу.',
 'sr-RS', 0.90, 'positive', 5, 9, true, md5('Спремни смо за дугорочну сарадњу.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Конкурентна цена', 'Цене су конкурентне у односу на квалитет.',
 'sr-RS', 0.84, 'positive', 4, 8, true, md5('Цене су конкурентне у односу на квалитет.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'suggestion', 'survey',
 'Интеграције', 'Више интеграција са другим системима.',
 'sr-RS', 0.48, 'neutral', 4, 6, true, md5('Више интеграција са другим системима.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Креативност', 'Тим показује високу креативност.',
 'sr-RS', 0.87, 'positive', 5, 8, true, md5('Тим показује високу креативност.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'social',
 'Релативност', 'Увек испуњавају дата обећања.',
 'sr-RS', 0.89, 'positive', 5, 9, true, md5('Увек испуњавају дата обећања.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Индивидуални приступ', 'Прилагођавају се нашим специфичним потребама.',
 'sr-RS', 0.91, 'positive', 5, 9, true, md5('Прилагођавају се нашим специфичним потребама.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Техничко знање', 'Имају одлично техничко знање.',
 'sr-RS', 0.94, 'positive', 5, 10, true, md5('Имају одлично техничко знање.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'suggestion', 'survey',
 'Документација', 'Документација би могла да буде детаљнија.',
 'sr-RS', 0.52, 'neutral', 4, 7, true, md5('Документација би могла да буде детаљнија.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Стабилност', 'Систем је веома стабилан.',
 'sr-RS', 0.88, 'positive', 5, 8, true, md5('Систем је веома стабилан.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'social',
 'Инновације', 'Константно уводе иновације.',
 'sr-RS', 0.92, 'positive', 5, 9, true, md5('Константно уводе иновације.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'website',
 'Комплетно решење', 'Нуде комплетна решења за наше потребе.',
 'sr-RS', 0.90, 'positive', 5, 9, true, md5('Нуде комплетна решења за наше потребе.')),

((SELECT companies_id FROM companies WHERE tax_id = '123456789'),
 NULL, 'review', 'email',
 'Експертиза', 'Имају велику експертизу у својој области.',
 'sr-RS', 0.93, 'positive', 5, 9, true, md5('Имају велику експертизу у својој области.'));

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    feedback_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO feedback_count FROM customer_feedback;
    RAISE NOTICE 'Customer Feedback Count: %', feedback_count;

    IF feedback_count >= 50 THEN
        RAISE NOTICE '✅ CUSTOMER FEEDBACK: TARGET ACHIEVED (50+ records: %)', feedback_count;
    ELSE
        RAISE NOTICE '❌ CUSTOMER FEEDBACK: TARGET NOT ACHIEVED (Current: %, Need: 50+)', feedback_count;
    END IF;
END $$;
