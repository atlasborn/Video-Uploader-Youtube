const fs = require("fs")
const express = require("express")
const google = require('googleapis').google
const youtube = google.youtube({ version: 'v3' })
const path = require('path')
const OAuth2 = google.auth.OAuth2


async function robot()
{
    await AutenticantionOAuth()
    const videoContent = await require(path.join(__dirname, 'media', 'response.json'))
    const videoInformation = await UploadVideo(videoContent)
    await SetThumbnail(videoInformation, content= videoContent)


    async function AutenticantionOAuth(){
        const webServer = await startWebServer()
        const OAuthClient = await createOAuthClient()
        requestUserContent(OAuthClient)
        // await waitForGoogleCallback()
        const authorizationToken =  await waitForGoogleCallback(webServer)
        await requestGoogleFOrAcessTokens(OAuthClient,authorizationToken)
        await SetGlobalGoogleAuthentication(OAuthClient)
        await stopWebServer(webServer)
        async function startWebServer(){
            return new Promise((resolve, reject) => {
                const port = 5000
                const app = express()

                const server = app.listen(port, () => {
                    console.log(`Server is running in  http://localhost:${port}`)
                
                    resolve({app, server})
                })
            })
        }

        async function createOAuthClient(){
            const credentials = require(path.join(__dirname, 'credentials', 'google-youtube.json'))
            const OAuthClient = new OAuth2 (
                credentials.web.client_id,
                credentials.web.client_secret,
                credentials.web.redirect_uris[0],
            )
                
            return OAuthClient
        }

        function requestUserContent(OAuthClient){
            const consentUrl = OAuthClient.generateAuthUrl({
                acess_type :'offline',
                scope: ['https://www.googleapis.com/auth/youtube'],

            })

            console.log(`> Please Give You Consent: ${consentUrl}`)
        }

        async function waitForGoogleCallback(webServer){
            return new Promise((resolve, reject) => {
                console.log('Wait For Use Consent....')

                webServer.app.get('/oauth2callback', (req, res) => {
                    const authCode = req.query.code
                    console.log(`> Consent Given ${authCode}`)

                    res.send('<h1>Thanks!</h1><p>Now you can close this tab.</p>')
                    resolve(authCode)
                })
            })
            
        }
        
        function requestGoogleFOrAcessTokens(OAuthClient, authorizationToken){
            return new Promise((resolve, reject) => {
                OAuthClient.getToken(authorizationToken, (error, tokens)=> {
                    if (error){
                        return reject(error)
                    }
                    
                    console.log('> Acess Tokens Receveid')

                    OAuthClient.setCredentials(tokens)
                    resolve()
                }) 
            }
        )
        }
        function SetGlobalGoogleAuthentication(OAuthClient){
            google.options({
                auth : OAuthClient
            })
        }

        async function stopWebServer(webServer){
            return new Promise((resolve, reject) => {
                webServer.server.close(() => {
                    resolve()
                })
            })
            
        }
    }


    async function UploadVideo(content){
        const videoFilePath = content.video_path
        const videoFileSize = fs.statSync(videoFilePath).size
        const videoTitle = content.title
        const videoDescription = content.description
        const videoTags = content.tags
        const videoCategory = content.category // 10 = Music
        const videoPrivacy = content.privacity


        const requestParameters = {
            "part": 'snippet, status',
            requestBody: {
                snippet: {
                    title: videoTitle,
                    description: videoDescription,
                    tags: videoTags,
                    categoryId: videoCategory
                    
                },
                status: {
                    privacyStatus: videoPrivacy //private, public, unlisted
                }
            },

            media: {
                body: fs.createReadStream(videoFilePath)
            }

        }

        const youtubeResponse =  await youtube.videos.insert(requestParameters, {
            onUploadProgress: onUploadProgress
        })

        console.log(`> Video available at: https://youtu.be/${youtubeResponse.data.id}`)
        return youtubeResponse.data

        function onUploadProgress(event){
            const progress = Math.round((event.bytesRead / videoFileSize) * 100)
            console.log(`> ${progress}% completed`)
        }
    }

    async function SetThumbnail(videoInformation, content){
        const videoId = videoInformation.id
        const videoThumbnailFilePath = content['thumbnail_path']

        const requestParameters = {
            videoId: videoId,
            media: {
                mimeType: 'image/jpeg',
                body: fs.createReadStream(videoThumbnailFilePath)
            }
        }

        const YoutubeResponse = await youtube.thumbnails.set(requestParameters)
        console.log('> Thumbnail uploaded')
    }
}
module.exports = robot

robot()
