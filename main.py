import pandas as pd
import numpy as np

'''
Member CSV format:
Columns: 
1. Full Name
2. Full Discord Tag (***#1234)
3. Email
4. Premade Role
5. Are you already part of a pre-made pitched team?	
6. Which team are you part of as a pre-made member?
7. 1st choice
8. 2nd choice
9. 3rd choice	
10. Role [1st Choice]
11. Role [2nd Choice]
12. Role [3rd Choice]

Team Lead CSV format:
Columns: 
1. Full Discord Tag (***#1234)
2. Game
3. Position
'''

PRIMARY = "Primary role"
NO_PREFERENCE = "No Preference"
ANY_TEAM = "Put me on any team"
NO_OTHER_TEAMS = "If I do not receive my previous choice, do not assign me to a team."


def main(member_csv, teamlead_csv):
    team_assignments = []

    member_df = pd.read_csv(member_csv)
    teamlead_df = pd.read_csv(teamlead_csv)

    # Get any member list
    get_all_any_teams(member_df)

    # Assign all premades
    for index, row in member_df.iterrows():

        # assign all pre-mades
        if not pd.isna(row.iloc[5]):
            team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[5], row.iloc[3], "Pre-made"])
            teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
            member_df = member_df.drop(index)

        # Otherwise Check for team lead requests
        else:
            for index2, row2 in teamlead_df.iterrows():
                # Check if discords are the same and their first pick is the same (including roles)
                if row2.iloc[0] == row.iloc[1] and row2.iloc[1] == row.iloc[6]:

                    # If the role wanted is in the row list, immediately add
                    if row2.iloc[2] in row.iloc[9]:
                        # Adds Name, Discord Tag, 1st Choice Game, Requested Role
                        team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[6], row2.iloc[2], "Requested"])
                        teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
                        member_df = member_df.drop(index)

                    # Roles don't match! Alert user!
                    else:
                        print(f"{row.iloc[0]} wants a different role for {row.iloc[6]}! Requested to be {row.iloc[9]} but team lead wants {row2.iloc[2]}")

    # Assign everyone else their first choice
    for index, row in member_df.iterrows():
        # Adds Name, Discord Tag, 1st Choice Game, 1st Choice Role
        team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[6], row.iloc[9], "Student First Choice"])
        teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
        pass

    # Save remaining team lead choices for inspection later
    teamlead_df.to_csv("leftover_team_choices.csv")

    # Convert to csv and sort
    nparray = np.array(team_assignments)
    pass1_csv = pd.DataFrame(nparray)
    pass1_csv = pass1_csv.set_axis(['Name', 'Discord', 'Game', 'Position', 'Reason'], axis=1)
    pass1_csv = pass1_csv.sort_values(['Game', 'Reason', 'Position', 'Name'])
    pass1_csv.to_csv("out.csv")


def get_all_any_teams(member_df):
    '''
    writes a csv with all members who put down any team in any choice

    :param member_df: dataframe of members
    :return: nothing
    '''
    any_team_members = []

    # iterate through all members and make a list of all any teams
    for index, row in member_df.iterrows():
        if row.iloc[6] == ANY_TEAM:
            # Adds Name, Discord Tag, which choice is any choice
            any_team_members.append([row.iloc[0], row.iloc[1], "1st Choice Any Choice"])
        elif row.iloc[7] == ANY_TEAM:
            any_team_members.append([row.iloc[0], row.iloc[1], "2nd Choice Any Choice"])
        elif row.iloc[8] == ANY_TEAM:
            any_team_members.append([row.iloc[0], row.iloc[1], "3rd Choice Any Choice"])
        # Convert to csv and sort
    nparray = np.array(any_team_members)
    pass1_csv = pd.DataFrame(nparray)
    pass1_csv = pass1_csv.set_axis(['Name', 'Discord', 'Any team Choice'], axis=1)
    pass1_csv = pass1_csv.sort_values(['Any team Choice', 'Name'])
    pass1_csv.to_csv("AnyChoicePeople.csv")

def drop_from_csv(df, discord):
    '''
    drops a particular discord from a team lead dataframe

    :param df: team lead dataframe
    :param discord: discord of person to remove from team lead list
    :return: new dataframe without that person
    '''

    for index, row in df.iterrows():
        if row.iloc[0] == discord:
            df = df.drop(index)
    return df


if __name__ == '__main__':
    main('Spring 2024 Game Sign Up Form (Responses) - Sort Form.csv', 'Spring 2024 Team Lead Mixer Sheet - Final Mixer Sheet.csv')

