import boto3
import csv

def user_import(event, context):
    region='us-east-1'
    recList=[]
    try:            
        s3=boto3.client('s3')            
        dyndb = boto3.client('dynamodb', region_name=region)
        confile= s3.get_object(Bucket='cs410-movies', Key='users.csv')
        recList = confile['Body'].read().decode().split('\n')
        csv_reader = csv.reader(recList, delimiter='|', quotechar='"')
        for row in csv_reader:
            id = row[0]
            age = row[1]
            gender = row[2]
            occupation = row[3]
            zip = row[4]
            response = dyndb.put_item(
                TableName='Users',
                Item={
                'id' : {'N':str(id)},
                'age': {'N':str(age)},
                'gender': {'S':str(gender)},
                'occupation': {'S':str(occupation)},
                'zip': {'S':str(zip)},
                }
            )
        print('Put succeeded:')
    except Exception as e:
        print (str(e))

def rating_import(event, context):
    region='us-east-1'
    recList=[]
    try:            
        s3=boto3.client('s3')            
        dyndb = boto3.client('dynamodb', region_name=region)
        confile= s3.get_object(Bucket='cs410-movies', Key='ratings.csv')
        recList = confile['Body'].read().decode().split('\n')
        csv_reader = csv.reader(recList, delimiter='|', quotechar='"')
        for row in csv_reader:
            userId = row[0]
            movieId = row[1]
            rating = row[2]
            timestamp = row[3]
            response = dyndb.put_item(
                TableName='Ratings',
                Item={
                'userId' : {'N':str(userId)},
                'movieId': {'N':str(movieId)},
                'rating': {'N':str(rating)},
                'timestamp': {'N':str(timestamp)},
                }
            )
        print('Put succeeded:')
    except Exception as e:
        print (str(e))


def movie_import(event, context):
    region='us-east-1'
    recList=[]
    try:            
        s3=boto3.client('s3')            
        dyndb = boto3.client('dynamodb', region_name=region)
        confile= s3.get_object(Bucket='cs410-movies', Key='movies.csv')
        recList = confile['Body'].read().decode('latin-1').split('\n')
        csv_reader = csv.reader(recList, delimiter='|', quotechar='"')
        for row in csv_reader:
            id = row[0]
            movie_title = row[1]
            release_date = row[2]
            video_release_date = row[3]
            IMDb_URL = row[4]
            unknown = row[5]
            Action = row[6]
            Adventure = row[7]
            Animation = row[8]
            Children = row[9]
            Comedy = row[10]
            Crime = row[11]
            Documentary = row[12]
            Drama = row[13]
            Fantasy = row[14]
            Film_Noir  = row[15]
            Horror = row[16]
            Musical = row[17]
            Mystery = row[18]
            Romance = row[19]
            Sci_Fi = row[20]
            Thriller = row[21]
            War = row[22]
            Western = row[23]
            item = {}
            item['id'] = {'N':str(id)}
            item['movie_title'] = {'S':str(movie_title)} if movie_title else {'NULL': True}
            item['release_date'] = {'S': str(release_date)} if release_date else {'NULL': True}
            item['video_release_date'] = {'S': str(video_release_date)} if video_release_date else {'NULL': True}
            item['IMDb_URL'] = {'S': str(IMDb_URL)} if IMDb_URL else {'NULL': True}
            item['unknown'] = {'N': str(unknown)} if unknown else {'NULL': True}
            item['Action'] = {'N': str(Action)} if Action else {'NULL': True}
            item['Adventure'] = {'N': str(Adventure)} if Adventure else {'NULL': True}
            item['Animation'] = {'N': str(Animation)} if Animation else {'NULL': True}
            item['Children'] = {'N': str(Children)} if Children else {'NULL': True}
            item['Comedy'] = {'N': str(Comedy)} if Comedy else {'NULL': True}
            item['Crime'] = {'N': str(Crime)} if Crime else {'NULL': True}
            item['Documentary'] = {'N': str(Documentary)} if Documentary else {'NULL': True}
            item['Drama'] = {'N': str(Drama)} if Drama else {'NULL': True}
            item['Fantasy'] = {'N': str(Fantasy)} if Fantasy else {'NULL': True}
            item['Film_Noir'] = {'N': str(Film_Noir)} if Film_Noir else {'NULL': True}
            item['Horror'] = {'N': str(Horror)} if Horror else {'NULL': True}
            item['Musical'] = {'N': str(Musical)} if Musical else {'NULL': True}
            item['Mystery'] = {'N': str(Mystery)} if Mystery else {'NULL': True}
            item['Romance'] = {'N': str(Romance)} if Romance else {'NULL': True}
            item['Sci_Fi'] = {'N': str(Sci_Fi)} if Sci_Fi else {'NULL': True}
            item['Thriller'] = {'N': str(Thriller)} if Thriller else {'NULL': True}
            item['War'] = {'N': str(War)} if War else {'NULL': True}
            item['Western'] = {'N': str(Western)} if Western else {'NULL': True}
            response = dyndb.put_item(
                TableName='Movies',
                Item=item
            )
        print('Put succeeded:')
    except Exception as e:
        print (str(e))