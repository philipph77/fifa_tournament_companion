-- Authentification --
INSERT INTO user (UserName, Password)
VALUES
  (
  'johndoe77',
  'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'
  );
INSERT INTO gamer (UserID, FirstName, LastName, TeamName)
VALUES
  (
  1,
  'John',
  'Doe',
  'Myteam 1903 e.V.'
  );