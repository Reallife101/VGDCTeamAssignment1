import pandas as pd
import numpy as np

'''
Member CSV format:
Columns: 
1. Full Name
2. Full Discord Tag (***#1234)
3. Primary Role
4. Secondary Role
5. Are you already part of a pre-made pitched team?	
6. Which team are you part of as a pre-made member?
7. 1st choice
8. 2nd choice
9. 3rd choice	
10. Choices for (Primary or Secondary Role) [1st Choice]
11. Choices for (Primary or Secondary Role) [2nd Choice]
12. Choices for (Primary or Secondary Role) [3rd Choice]

Team Lead CSV format:
Columns: 
1. Full Discord Tag (***#1234)
2. Game
3. Position
'''

PRIMARY = "Primary role"
NO_PREFERENCE = "No Preference"


def main(member_csv, teamlead_csv):
    team_assignments = []

    member_df = pd.read_csv(member_csv)
    teamlead_df = pd.read_csv(teamlead_csv)

    # Assign all premades
    for index, row in member_df.iterrows():

        # assign all pre-mades
        if not pd.isna(row[5]):
            team_assignments.append([row[0], row[1], row[5], row[2], "Pre-made"])
            teamlead_df = drop_from_csv(teamlead_df, row[1])
            member_df = member_df.drop(index)

        # Otherwise Check for team lead requests
        else:
            for index2, row2 in teamlead_df.iterrows():
                # Check if discords are the same and their first pick is the same (including roles)
                if row2[0] == row[1] and row2[1] == row[6]:

                    # If no preference, check either primary or secondary roles
                    if (row[9] == NO_PREFERENCE and (row2[2] == row[2] or row2[2] == row[3])):
                        team_assignments.append([row[0], row[1], row[6], row2[2], "Requested"])
                        teamlead_df = drop_from_csv(teamlead_df, row[1])
                        member_df = member_df.drop(index)

                    # Otherwise check primary or secondary roles match
                    elif row2[2] == (row[2] if row[9] == PRIMARY else row[3]):
                        team_assignments.append([row[0], row[1], row[6], row[2] if row[9] == PRIMARY else row[3], "Requested"])
                        teamlead_df = drop_from_csv(teamlead_df, row[1])
                        member_df = member_df.drop(index)

                    # Leftover means roles don't match! Alert user!
                    else:
                        print(
                            f"{row[0]} wants a different role for {row[6]}! Requested to be {row[2] if row[9] == PRIMARY else row[3]} but team lead wants {row2[2]}")

    # Assign everyone their first choice
    for index, row in member_df.iterrows():
        team_assignments.append([row[0], row[1], row[6], row[2] if row[9] == PRIMARY else row[3], "Student First Choice"])
        teamlead_df = drop_from_csv(teamlead_df, row[1])
        pass

    # Save remaining team lead choices for inspection later
    teamlead_df.to_csv("leftover_team_choices.csv")

    # Convert to csv and sort
    nparray = np.array(team_assignments)
    pass1_csv = pd.DataFrame(nparray)
    pass1_csv = pass1_csv.set_axis(['Name', 'Discord', 'Game', 'Position', 'Reason'], axis=1)
    pass1_csv = pass1_csv.sort_values(['Game', 'Reason', 'Position', 'Name'])
    pass1_csv.to_csv("out.csv")


def drop_from_csv(df, discord):
    '''
    drops a particular discord from a team lead dataframe

    :param df: team lead dataframe
    :param discord: discord of person to remove from team lead list
    :return: new dataframe without that person
    '''

    for index, row in df.iterrows():
        if row[0] == discord:
            df = df.drop(index)
    return df


if __name__ == '__main__':
    main('test.csv', 'teamlead.csv')
