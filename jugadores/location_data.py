# Datos de estados y ciudades por país para selects dependientes

LOCATION_DATA = {
    'USA': {
        'states': [
            ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
            ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
            ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'),
            ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
            ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
            ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
            ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'),
            ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
            ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
            ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
            ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'),
            ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
            ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
            ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
            ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
            ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
            ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
        ],
        'cities': {
            'CA': ['Los Angeles', 'San Diego', 'San Francisco', 'San Jose'],
            'TX': ['Houston', 'San Antonio', 'Dallas', 'Austin'],
            'FL': ['Jacksonville', 'Miami', 'Tampa', 'Orlando'],
            'NY': ['New York City', 'Buffalo', 'Rochester'],
            'IL': ['Chicago', 'Aurora', 'Naperville'],
        }
    },
    'MEX': {
        'states': [
            ('AGU', 'Aguascalientes'), ('BCN', 'Baja California'),
            ('BCS', 'Baja California Sur'), ('CAM', 'Campeche'),
            ('CHP', 'Chiapas'), ('CHH', 'Chihuahua'), ('COA', 'Coahuila'),
            ('COL', 'Colima'), ('DIF', 'Ciudad de Mexico'),
            ('DUR', 'Durango'), ('GUA', 'Guanajuato'), ('GRO', 'Guerrero'),
            ('HID', 'Hidalgo'), ('JAL', 'Jalisco'), ('MEX', 'Mexico'),
            ('MIC', 'Michoacan'), ('MOR', 'Morelos'), ('NAY', 'Nayarit'),
            ('NLE', 'Nuevo Leon'), ('OAX', 'Oaxaca'), ('PUE', 'Puebla'),
            ('QUE', 'Queretaro'), ('ROO', 'Quintana Roo'),
            ('SLP', 'San Luis Potosi'), ('SIN', 'Sinaloa'), ('SON', 'Sonora'),
            ('TAB', 'Tabasco'), ('TAM', 'Tamaulipas'), ('TLA', 'Tlaxcala'),
            ('VER', 'Veracruz'), ('YUC', 'Yucatan'), ('ZAC', 'Zacatecas'),
        ],
        'cities': {
            'DIF': ['Ciudad de Mexico'],
            'JAL': ['Guadalajara', 'Zapopan'],
            'NLE': ['Monterrey', 'San Pedro Garza Garcia'],
            'PUE': ['Puebla'],
            'QUE': ['Queretaro'],
            'ROO': ['Cancun', 'Playa del Carmen'],
            'VER': ['Veracruz', 'Xalapa'],
            'SON': ['Hermosillo', 'Nogales'],
            'CHH': ['Chihuahua', 'Ciudad Juarez'],
            'SIN': ['Culiacan', 'Mazatlan'],
        }
    },
    'DOM': {
        'states': [
            ('DN', 'Distrito Nacional'), ('AZ', 'Azua'), ('BA', 'Barahona'),
            ('CL', 'La Altagracia'), ('CR', 'La Romana'), ('DU', 'Duarte'),
            ('EL', 'Elias Pina'), ('ES', 'Espaillat'), ('HN', 'Hato Mayor'),
            ('IN', 'Independencia'), ('MN', 'Maria Trinidad Sanchez'),
            ('MC', 'Monte Cristi'), ('MN2', 'Monte Plata'), ('PA', 'La Vega'),
            ('PR', 'Peravia'), ('PM', 'Pedernales'), ('PP', 'Puerto Plata'),
            ('SM', 'Samana'), ('SC', 'Sanchez Ramirez'), ('SN', 'Santiago'),
            ('SD', 'Santo Domingo'), ('SL', 'San Cristobal'),
            ('SP', 'San Pedro de Macoris'), ('ST', 'Santiago Rodriguez'),
            ('VA', 'Valverde'),
        ],
        'cities': {
            'DN': ['Santo Domingo'],
            'SN': ['Santiago de los Caballeros'],
            'CL': ['Punta Cana', 'Higuey'],
            'PR': ['Bani'],
            'PP': ['Puerto Plata'],
            'SM': ['Samana'],
            'CR': ['La Romana'],
            'SD': ['Boca Chica', 'Santo Domingo Este'],
        }
    },
    'CUB': {
        'states': [
            ('HAV', 'La Habana'), ('MAT', 'Matanzas'), ('VCL', 'Villa Clara'),
            ('CIU', 'Cienfuegos'), ('SSP', 'Sancti Spiritus'),
            ('CMG', 'Camaguey'), ('LTU', 'Las Tunas'), ('HOL', 'Holguin'),
            ('GRM', 'Granma'), ('SCT', 'Santiago de Cuba'),
            ('GUA', 'Guantanamo'), ('ART', 'Artemisa'),
            ('MYB', 'Mayabeque'), ('IJU', 'Isla de la Juventud'),
        ],
        'cities': {
            'HAV': ['La Habana'],
            'SCT': ['Santiago de Cuba'],
            'HOL': ['Holguin'],
            'CMG': ['Camaguey'],
            'VCL': ['Santa Clara'],
            'CIU': ['Cienfuegos'],
            'MAT': ['Matanzas'],
            'GRM': ['Bayamo'],
        }
    },
    'VEN': {
        'states': [
            ('AM', 'Amazonas'), ('AN', 'Anzoategui'), ('AR', 'Aragua'),
            ('AP', 'Apure'), ('BA', 'Barinas'), ('BO', 'Bolivar'),
            ('CA', 'Carabobo'), ('CO', 'Cojedes'), ('DA', 'Delta Amacuro'),
            ('DC', 'Distrito Capital'), ('FA', 'Falcon'), ('GU', 'Guarico'),
            ('LA', 'Lara'), ('ME', 'Merida'), ('MI', 'Miranda'),
            ('MO', 'Monagas'), ('NE', 'Nueva Esparta'), ('PO', 'Portuguesa'),
            ('SU', 'Sucre'), ('TA', 'Tachira'), ('TR', 'Trujillo'),
            ('VA', 'Vargas'), ('YA', 'Yaracuy'), ('ZU', 'Zulia'),
        ],
        'cities': {
            'DC': ['Caracas'],
            'ZU': ['Maracaibo'],
            'CA': ['Valencia'],
            'AR': ['Maracay'],
            'TA': ['San Cristobal'],
            'LA': ['Barquisimeto'],
            'ME': ['Merida'],
            'AN': ['Barcelona'],
            'SU': ['Cumana'],
            'BO': ['Ciudad Bolivar'],
        }
    },
    'COL': {
        'states': [
            ('AMA', 'Amazonas'), ('ANT', 'Antioquia'), ('ARA', 'Arauca'),
            ('ATL', 'Atlantico'), ('BOL', 'Bolivar'), ('BOY', 'Boyaca'),
            ('CAL', 'Caldas'), ('CAQ', 'Caqueta'), ('CAS', 'Casanare'),
            ('CAU', 'Cauca'), ('CES', 'Cesar'), ('CHI', 'Choco'),
            ('COR', 'Cordoba'), ('CUN', 'Cundinamarca'), ('GUA', 'Guainia'),
            ('GUV', 'Guaviare'), ('HUI', 'Huila'), ('LAG', 'La Guajira'),
            ('MAG', 'Magdalena'), ('MET', 'Meta'), ('NAR', 'Narino'),
            ('NSA', 'Norte de Santander'), ('PUT', 'Putumayo'),
            ('QUI', 'Quindio'), ('RIS', 'Risaralda'), ('SAN', 'Santander'),
            ('SAP', 'Sucre'), ('TOL', 'Tolima'), ('VAC', 'Valle del Cauca'),
            ('VAU', 'Vaupes'), ('VIC', 'Vichada'),
        ],
        'cities': {
            'CUN': ['Bogota'],
            'ANT': ['Medellin', 'Envigado'],
            'VAC': ['Cali', 'Santiago de Cali'],
            'ATL': ['Barranquilla'],
            'BOL': ['Cartagena'],
            'SAN': ['Bucaramanga'],
            'CES': ['Valledupar'],
            'RIS': ['Pereira'],
            'QUI': ['Armenia'],
        }
    },
    'ARG': {
        'states': [
            ('BA', 'Buenos Aires'), ('CF', 'Ciudad Autonoma de Buenos Aires'),
            ('CT', 'Catamarca'), ('CC', 'Chaco'), ('CH', 'Chubut'),
            ('CB', 'Cordoba'), ('CN', 'Corrientes'), ('ER', 'Entre Rios'),
            ('FM', 'Formosa'), ('JU', 'Jujuy'), ('LP', 'La Pampa'),
            ('LR', 'La Rioja'), ('MZ', 'Mendoza'), ('MI', 'Misiones'),
            ('NQ', 'Neuquen'), ('RN', 'Rio Negro'), ('SA', 'Salta'),
            ('SJ', 'San Juan'), ('SL', 'San Luis'), ('SC', 'Santa Cruz'),
            ('SF', 'Santa Fe'), ('SE', 'Santiago del Estero'),
            ('TF', 'Tierra del Fuego'), ('TU', 'Tucuman'),
        ],
        'cities': {
            'CF': ['Buenos Aires'],
            'BA': ['La Plata', 'Mar del Plata'],
            'CB': ['Cordoba'],
            'SF': ['Rosario', 'Santa Fe'],
            'MZ': ['Mendoza'],
            'TU': ['San Miguel de Tucuman'],
            'ER': ['Parana'],
            'CH': ['Comodoro Rivadavia'],
        }
    },
    'BRA': {
        'states': [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapa'),
            ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceara'),
            ('DF', 'Distrito Federal'), ('ES', 'Espirito Santo'),
            ('GO', 'Goias'), ('MA', 'Maranhao'), ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
            ('PA', 'Para'), ('PB', 'Paraiba'), ('PR', 'Parana'),
            ('PE', 'Pernambuco'), ('PI', 'Piaui'), ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondonia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'Sao Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
        ],
        'cities': {
            'SP': ['Sao Paulo', 'Campinas', 'Guarulhos'],
            'RJ': ['Rio de Janeiro'],
            'MG': ['Belo Horizonte', 'Uberlandia'],
            'RS': ['Porto Alegre'],
            'PR': ['Curitiba'],
            'BA': ['Salvador'],
            'DF': ['Brasilia'],
            'CE': ['Fortaleza'],
            'PE': ['Recife'],
        }
    },
    'CAN': {
        'states': [
            ('AB', 'Alberta'), ('BC', 'British Columbia'),
            ('MB', 'Manitoba'), ('NB', 'New Brunswick'),
            ('NL', 'Newfoundland and Labrador'), ('NS', 'Nova Scotia'),
            ('NT', 'Northwest Territories'), ('NU', 'Nunavut'),
            ('ON', 'Ontario'), ('PE', 'Prince Edward Island'),
            ('QC', 'Quebec'), ('SK', 'Saskatchewan'), ('YT', 'Yukon'),
        ],
        'cities': {
            'ON': ['Toronto', 'Ottawa', 'Hamilton'],
            'QC': ['Montreal', 'Quebec City'],
            'BC': ['Vancouver', 'Victoria'],
            'AB': ['Calgary', 'Edmonton'],
            'MB': ['Winnipeg'],
            'SK': ['Saskatoon'],
        }
    },
    'PRI': {
        'states': [
            ('SJ', 'San Juan'), ('AG', 'Aguadilla'), ('AR', 'Arecibo'),
            ('CA', 'Caguas'), ('FA', 'Fajardo'), ('GU', 'Guayama'),
            ('MA', 'Mayaguez'), ('PO', 'Ponce'), ('BA', 'Bayamon'),
            ('CA2', 'Carolina'),
        ],
        'cities': {
            'SJ': ['San Juan'],
            'PO': ['Ponce'],
            'MA': ['Mayaguez'],
            'BA': ['Bayamon'],
            'CA2': ['Carolina'],
            'AR': ['Arecibo'],
        }
    },
    'PAN': {
        'states': [
            ('BDM', 'Bocas del Toro'), ('COC', 'Cocle'), ('COL', 'Colon'),
            ('CHR', 'Chiriqui'), ('DAR', 'Darien'), ('ERR', 'Herrera'),
            ('LOS', 'Los Santos'), ('NGO', 'Ngabe Bugle'), ('PAN', 'Panama'),
            ('VDE', 'Veraguas'), ('GKY', 'Guna Yala'), ('EMB', 'Embera'),
            ('KUN', 'Kuna Yala'),
        ],
        'cities': {
            'PAN': ['Panama City'],
            'COL': ['Colon'],
            'CHR': ['David'],
            'COC': ['Penonome'],
        }
    },
    'NIC': {
        'states': [
            ('AN', 'Atlantico Norte'), ('AS', 'Atlantico Sur'),
            ('BO', 'Boaco'), ('CA', 'Carazo'), ('CI', 'Chinandega'),
            ('CO', 'Chontales'), ('ES', 'Esteli'), ('GR', 'Granada'),
            ('JN', 'Jinotega'), ('LE', 'Leon'), ('MD', 'Madriz'),
            ('MN', 'Managua'), ('MS', 'Masaya'), ('MT', 'Matagalpa'),
            ('NS', 'Nueva Segovia'), ('RJ', 'Rio San Juan'),
            ('RI', 'Rivas'), ('SJ', 'San Juan River'),
        ],
        'cities': {
            'MN': ['Managua'],
            'LE': ['Leon'],
            'GR': ['Granada'],
            'CI': ['Chinandega'],
            'ES': ['Esteli'],
            'MT': ['Matagalpa'],
        }
    },
    'HND': {
        'states': [
            ('AT', 'Atlantida'), ('CH', 'Choluteca'), ('CL', 'Colon'),
            ('CM', 'Comayagua'), ('CP', 'Copan'), ('CR', 'Cortes'),
            ('EP', 'El Paraiso'), ('FM', 'Francisco Morazan'),
            ('GD', 'Gracias a Dios'), ('IN', 'Intibuca'),
            ('IB', 'Islas de la Bahia'), ('LP', 'La Paz'),
            ('LM', 'Lempira'), ('OC', 'Ocotepeque'), ('OL', 'Olancho'),
            ('SB', 'Santa Barbara'), ('VA', 'Valle'), ('YO', 'Yoro'),
        ],
        'cities': {
            'FM': ['Tegucigalpa'],
            'CR': ['San Pedro Sula'],
            'AT': ['La Ceiba'],
            'CH': ['Choluteca'],
        }
    },
    'GTM': {
        'states': [
            ('AV', 'Alta Verapaz'), ('BV', 'Baja Verapaz'),
            ('CM', 'Chimaltenango'), ('CQ', 'Chiquimula'),
            ('ES', 'El Progreso'), ('GU', 'Guatemala'), ('HU', 'Huehuetenango'),
            ('IZ', 'Izabal'), ('JA', 'Jalapa'), ('JU', 'Jutiapa'),
            ('PE', 'Peten'), ('QZ', 'Quetzaltenango'), ('QC', 'Quiche'),
            ('RE', 'Retalhuleu'), ('SA', 'Sacatepequez'), ('SM', 'San Marcos'),
            ('SO', 'Solola'), ('SR', 'Suchitepequez'), ('TO', 'Totonicapan'),
            ('ZA', 'Zacapa'),
        ],
        'cities': {
            'GU': ['Guatemala City'],
            'QZ': ['Quetzaltenango'],
            'ES': ['Mixco'],
            'SM': ['San Marcos'],
            'IZ': ['Puerto Barrios'],
        }
    },
    'SLV': {
        'states': [
            ('AH', 'Ahuachapan'), ('CA', 'Cabanas'), ('CH', 'Chalatenango'),
            ('CU', 'Cuscatlan'), ('LI', 'La Libertad'), ('PA', 'La Paz'),
            ('LM', 'La Union'), ('MO', 'Morazan'), ('SM', 'San Miguel'),
            ('SS', 'San Salvador'), ('SV', 'San Vicente'), ('SA', 'Santa Ana'),
            ('SO', 'Sonsonate'), ('US', 'Usulutan'),
        ],
        'cities': {
            'SS': ['San Salvador'],
            'SA': ['Santa Ana'],
            'SM': ['San Miguel'],
            'LI': ['Santa Tecla'],
            'SV': ['San Vicente'],
        }
    },
    'CRI': {
        'states': [
            ('SJ', 'San Jose'), ('AL', 'Alajuela'), ('CA', 'Cartago'),
            ('HE', 'Heredia'), ('GU', 'Guanacaste'), ('PU', 'Puntarenas'),
            ('LM', 'Limon'),
        ],
        'cities': {
            'SJ': ['San Jose'],
            'AL': ['Alajuela'],
            'HE': ['Heredia'],
            'CA': ['Cartago'],
            'LI': ['Limon'],
            'PU': ['Puntarenas'],
        }
    },
    'ECU': {
        'states': [
            ('AZ', 'Azuay'), ('BO', 'Bolivar'), ('CA', 'Canar'),
            ('CAR', 'Carchi'), ('CH', 'Chimborazo'), ('CO', 'Cotopaxi'),
            ('EU', 'El Oro'), ('ES', 'Esmeraldas'), ('GA', 'Galapagos'),
            ('GU', 'Guayas'), ('IM', 'Imbabura'), ('LO', 'Loja'),
            ('LR', 'Los Rios'), ('MA', 'Manabi'), ('MO', 'Morona Santiago'),
            ('NA', 'Napo'), ('PA', 'Pastaza'), ('PI', 'Pichincha'),
            ('TU', 'Tungurahua'), ('ZC', 'Zamora Chinchipe'),
        ],
        'cities': {
            'PI': ['Quito'],
            'GU': ['Guayaquil'],
            'AZ': ['Cuenca'],
            'MA': ['Portoviejo', 'Manta'],
            'EU': ['Machala'],
            'IM': ['Ibarra'],
            'LO': ['Loja'],
            'LR': ['Babahoyo'],
        }
    },
    'PER': {
        'states': [
            ('AMA', 'Amazonas'), ('ANC', 'Ancash'), ('APU', 'Apurimac'),
            ('ARE', 'Arequipa'), ('AYA', 'Ayacucho'), ('CAJ', 'Cajamarca'),
            ('CAL', 'Callao'), ('CUS', 'Cusco'), ('HUV', 'Huancavelica'),
            ('HUC', 'Huanuco'), ('ICA', 'Ica'), ('JUN', 'Junin'),
            ('LAL', 'La Libertad'), ('LAM', 'Lambayeque'), ('LIM', 'Lima'),
            ('LOR', 'Loreto'), ('MDD', 'Madre de Dios'), ('MOQ', 'Moquegua'),
            ('PAS', 'Pasco'), ('PIU', 'Piura'), ('PUN', 'Puno'),
            ('SAM', 'San Martin'), ('TAC', 'Tacna'), ('TUM', 'Tumbes'),
            ('UCA', 'Ucayali'),
        ],
        'cities': {
            'LIM': ['Lima'],
            'ARE': ['Arequipa'],
            'TRU': ['Trujillo'],
            'PIU': ['Piura'],
            'CUS': ['Cusco'],
            'CAL': ['Callao'],
            'ICA': ['Ica'],
            'JUN': ['Huancayo'],
            'CHI': ['Chiclayo'],
        }
    },
    'CHL': {
        'states': [
            ('AP', 'Arica y Parinacota'), ('TA', 'Tarapaca'),
            ('AN', 'Antofagasta'), ('AT', 'Atacama'), ('CO', 'Coquimbo'),
            ('VA', 'Valparaiso'), ('RM', 'Region Metropolitana'),
            ('OH', 'O\'Higgins'), ('MA', 'Maule'), ('BI', 'Biobio'),
            ('AR', 'Araucania'), ('LR', 'Los Rios'), ('LL', 'Los Lagos'),
            ('AI', 'Aysen'), ('MA2', 'Magallanes'),
        ],
        'cities': {
            'RM': ['Santiago'],
            'VA': ['Valparaiso', 'Vina del Mar'],
            'BI': ['Concepcion'],
            'AN': ['Antofagasta'],
            'TA': ['Iquique'],
            'CO': ['La Serena'],
            'AR': ['Temuco'],
        }
    },
    'BOL': {
        'states': [
            ('BEN', 'Beni'), ('COC', 'Cochabamba'), ('CHU', 'Chuquisaca'),
            ('LPZ', 'La Paz'), ('ORU', 'Oruro'), ('PAN', 'Pando'),
            ('POT', 'Potosi'), ('SCZ', 'Santa Cruz'), ('TAR', 'Tarija'),
        ],
        'cities': {
            'LPZ': ['La Paz'],
            'SCZ': ['Santa Cruz de la Sierra'],
            'COC': ['Cochabamba'],
            'CHU': ['Sucre'],
            'ORU': ['Oruro'],
        }
    },
    'URY': {
        'states': [
            ('AR', 'Artigas'), ('CA', 'Canelones'), ('CL', 'Cerro Largo'),
            ('CO', 'Colonia'), ('DU', 'Durazno'), ('FL', 'Flores'),
            ('FD', 'Florida'), ('LA', 'Lavalleja'), ('MA', 'Maldonado'),
            ('MO', 'Montevideo'), ('PA', 'Paysandu'), ('RN', 'Rio Negro'),
            ('RV', 'Rivera'), ('RO', 'Rocha'), ('SA', 'Salto'),
            ('SJ', 'San Jose'), ('SO', 'Soriano'), ('TA', 'Tacuarembo'),
            ('TT', 'Treinta y Tres'),
        ],
        'cities': {
            'MO': ['Montevideo'],
            'CA': ['Canelones'],
            'MA': ['Punta del Este'],
            'SA': ['Salto'],
            'PA': ['Paysandu'],
        }
    },
    'PRY': {
        'states': [
            ('ASU', 'Asuncion'), ('CON', 'Concepcion'), ('SAN', 'San Pedro'),
            ('COP', 'Cordillera'), ('GUA', 'Guaira'), ('CA', 'Caaguazu'),
            ('CAZ', 'Caazapa'), ('IT', 'Itapua'), ('MIS', 'Misiones'),
            ('PAR', 'Paraguari'), ('AL', 'Alto Parana'), ('CEN', 'Central'),
            ('NE', 'Nneembucu'), ('AME', 'Amambay'), ('CAN', 'Canindeyu'),
            ('BOQ', 'Boqueron'), ('PRE', 'Presidente Hayes'),
            ('ALTO', 'Alto Paraguay'),
        ],
        'cities': {
            'ASU': ['Asuncion'],
            'CEN': ['Luque', 'San Lorenzo'],
            'AL': ['Ciudad del Este'],
            'IT': ['Encarnacion'],
        }
    },
    'JAM': {
        'states': [
            ('KGN', 'Kingston'), ('STJ', 'St. James'), ('STT', 'St. Thomas'),
            ('CLA', 'Clarendon'), ('MAN', 'Manchester'), ('POR', 'Portland'),
            ('ANN', 'St. Ann'), ('HAN', 'Hanover'), ('WES', 'Westmoreland'),
            ('STC', 'St. Catherine'), ('STL', 'St. Elizabeth'),
            ('TR', 'Trelawny'), ('STM', 'St. Mary'), ('AND', 'St. Andrew'),
        ],
        'cities': {
            'KGN': ['Kingston'],
            'STJ': ['Montego Bay'],
            'STT': ['Port Maria'],
            'CLA': ['May Pen'],
        }
    },
    'HTI': {
        'states': [
            ('OU', 'Ouest'), ('NO', 'Nord'), ('NE', 'Nord-Est'),
            ('AN', 'Artibonite'), ('CE', 'Centre'), ('GR', 'Grand Anse'),
            ('NI', 'Nippes'), ('NO2', 'Nord-Ouest'), ('SD', 'Sud'),
            ('SE', 'Sud-Est'),
        ],
        'cities': {
            'OU': ['Port-au-Prince'],
            'AN': ['Gonaves'],
            'NO': ['Cap-Haitien'],
            'GR': ['Jeremie'],
        }
    },
    'TTO': {
        'states': [
            ('POS', 'Port of Spain'), ('SAN', 'San Fernando'),
            ('CHA', 'Chaguanas'), ('ARI', 'Arima'), ('PEN', 'Penal'),
            ('SIP', 'Siparia'), ('SCO', 'Scarborough'),
            ('PTF', 'Point Fortin'), ('ROX', 'Rio Claro'), ('COU', 'Couva'),
            ('TOB', 'Tobago'),
        ],
        'cities': {
            'POS': ['Port of Spain'],
            'SAN': ['San Fernando'],
            'CHA': ['Chaguanas'],
            'ARI': ['Arima'],
            'SCO': ['Scarborough'],
        }
    },
}
