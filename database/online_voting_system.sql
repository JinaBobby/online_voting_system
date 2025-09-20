USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$brL2yRkHGTXdL8Tc$66c26d47f069176aa5285db453c1c5745e8bfb930442b6d0c475c705b8f8b28f'
WHERE aadhar_number = '111111111111'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$WzXOKkJVUDhFpKKo$29943beb565636c6b606e4109e6bb20597a3e64ac3a0576896ce594ee214b026'
WHERE aadhar_number = '222222222222'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$kLaaQ3w4JvoYvGjn$93e7cebaee18557ef5f29c12ee95bce7b90a44896cb45973e6205d397ea0db45'
WHERE aadhar_number = '333333333333'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$5pmktbRIkFfeaiN5$7e2121efaaa0376c9e575bb5baa33e564e67b6433ab129931e1b439787bb2948'
WHERE aadhar_number = '444444444444'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$9cnZ9wMn713Pd4mR$3645d380d36840b807cc6c5af823c3b397ecdf80bef8be630936455ba17564ae'
WHERE aadhar_number = '555555555555'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$45dI45pmO5beYl7j$a8b93c564eec17e824b1972bdbd0d385e9c8ce9b2121f9b083e9ea56114bb4fc'
WHERE aadhar_number = '666666666666'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$BPGZPKM93G16wfAn$7781c26c0a80ebda7e1389aa4759a2d2ad80571583b7e1318ecec661598c9655'
WHERE aadhar_number = '777777777777'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$nfwy1hB4fCIerfXc$4f4c1ebad51be5d4dfccd6a4e753d041f72efa672891ab3f8ca33c84cabca20b'
WHERE aadhar_number = '888888888888'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$O7sFCxtLxSS5CCa2$63e4a83f712771e0c4f2c8ade2a0b120edc2d757f01f553e8f35a21f71161be2'
WHERE aadhar_number = '999999999999'; -- Use her Aadhar number for precise update

USE online_voting_db; -- Make sure you're using the correct database
UPDATE Voters
SET password_hash = 'pbkdf2:sha256:1000000$hRaXnASHfPMiKyYq$846bc1b67b7d3be0f920788de184b937626211894d2b138b2c809ed3f8ff5b2c'
WHERE aadhar_number = '000000000000'; -- Use her Aadhar number for precise update


USE online_voting_db; -- Make sure you're using the correct database

-- Update admin_user
UPDATE Admins
SET password_hash = 'pbkdf2:sha256:1000000$7UyhpAaiNszSWppP$1cc8376aacf029259dc3518cf5af26709e1df77891ab619816fad2a3b6cf4050'
WHERE username = 'admin1';

-- Update moderator
UPDATE Admins
SET password_hash = 'pbkdf2:sha256:1000000$CZoTxsk1ziBijD8R$2c7946e9f6507e077c45f3cdea8f18ee8f30a9ab746a93848160ec82ce3195f5'
WHERE username = 'admin2';

-- Update reporter
UPDATE Admins
SET password_hash = 'pbkdf2:sha256:1000000$3soQd8mH8aJmvQfq$ea72f2128d0be27c0a3c2d3ad5a0373d9c32710e2ddd2d87cef08b03c7a58211'
WHERE username = 'admin3';